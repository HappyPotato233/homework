import pandas as pd
import numpy as np

class AutoCleanDecision:
    def __init__(self, df):
        '''
        初始化自动清洗决策类
        :param df: 输入的DataFrame
        '''
        self.df = df.copy() # 用于中间处理
        self.df_raw = df.copy() # 用于做比较，写清洗报告
        self.col_missing_drop_threshold = 0.5
        self.iqr_scale = 1.5
        self.outlier_records = None
        
        # 记录清洗过程数据，用于生成报告
        self.original_shape = df.shape
        self.deleted_cols = []
        self.missing_stats = {}
        self.outlier_stats = {}
    
    def handle_missing_value(self):
        '''
            遍历每一列，根据缺失率执行不同策略
                决策逻辑：
            1. 计算缺失率：`missing_rate = 列缺失数 / 总行数`
            2. 规则 1 — 删除列：缺失率 > `col_missing_drop_threshold`，标记该列待删除
            3. 规则 2 — 中位数填充：数值列（`is_numeric_dtype`），用该列中位数填充
            4. 规则 3 — 占位填充：文本/分类列，用 `"未知/未填写"` 填充
            5. 批量删除标记的列
            输出**：打印每列缺失率、处理方式；返回处理后的 DataFrame
        '''
        # 查看表中每一列的缺失值
        # print("缺失值统计")
        # print(self.df.isnull().sum())
        delete_cols = [] # 记录待删除的列
        date_list = ['date','time','timestamp','dt'] # 日期/时间列关键字
        # 遍历每一列
        for col in [col for col in self.df.columns if self.df[col].isnull().sum() > 0]:
            # 计算缺失率
            missing_count = self.df[col].isnull().sum()
            missing_rate = missing_count / len(self.df)
            # 标记缺失率大于阈值的列（之所以不直接删除，是为了方便后续拓展）
            if missing_rate > self.col_missing_drop_threshold:
                delete_cols.append(col)
                print(f"标记缺失率超过阈值的列：{col}")
                self.missing_stats[col] = {"before": missing_rate, "after": None, "strategy": "删除列"}
            # 检查该列是否为日期/时间列（通过列名关键字判断）
            elif any(date in col.lower() for date in date_list):
                self.df[col] = self.df[col].ffill().bfill()
                print(f"用向前填充和向后填充处理时间列：{col}")
                print(f"{col}列一共填充 {missing_count} 个缺失值。")
                self.missing_stats[col] = {"before": missing_rate, "after": 0.0, "strategy": "前向填充+后向填充"}
            # 检查该列是否为数值列（排除布尔类型），如果是则用中位数填充
            elif pd.api.types.is_numeric_dtype(self.df[col]) and not pd.api.types.is_bool_dtype(self.df[col]):
                print(f"用中位数填充缺失值：{col}")
                print(f"{col}列一共填充 {missing_count} 个缺失值。")
                self.df[col] = self.df[col].fillna(self.df[col].median())
                self.missing_stats[col] = {"before": missing_rate, "after": 0.0, "strategy": "中位数填充"}
            # 检查该列是否为文本/分类列，如果是则用未知/未填写填充
            elif pd.api.types.is_string_dtype(self.df[col]) or pd.api.types.is_categorical_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna("未知/未填写")
                print(f"用未知/未填写填充缺失值：{col}")
                print(f"{col}列一共填充 {missing_count} 个缺失值。")
                self.missing_stats[col] = {"before": missing_rate, "after": 0.0, "strategy": "未知/未填写填充"}

        # 批量删除标记的列
        self.deleted_cols = delete_cols
        self.df.drop(columns=delete_cols, inplace=True)
        print(f"删除 {len(delete_cols)} 个缺失率超过阈值的列：{delete_cols}")
        return self.df

    def _get_numeric_cols(self):
        '''
            获取数值列（排除布尔类型）
            :return: 数值列名列表
        '''
        return [col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col]) and not pd.api.types.is_bool_dtype(self.df[col])]
    
    def _calc_iqr_bounds(self, col):
        '''
            计算 IQR 异常值上下限
            :param col: 数值列名
            :return: (lower, upper) 异常值上下限
        '''
        Q1 = self.df[col].quantile(0.25)
        Q3 = self.df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - self.iqr_scale * IQR
        if lower < 0:
            lower = 0
        upper = Q3 + self.iqr_scale * IQR
        return lower, upper
    
    def _build_outlier_records(self):
        '''
            构建异常值记录 DataFrame
            :return: None
        '''
        outlier_indices = set()
        outlier_reasons = {}
        
        for col in self._get_numeric_cols():
            lower, upper = self._calc_iqr_bounds(col)
            col_outliers = self.df[(self.df[col] < lower) | (self.df[col] > upper)].index
            for idx in col_outliers:
                val = self.df.loc[idx, col]
                reason = f"{col}列值{val}超出范围[{lower:.2f}, {upper:.2f}]"
                if idx in outlier_reasons:
                    outlier_reasons[idx] += "; " + reason
                else:
                    outlier_reasons[idx] = reason
                outlier_indices.add(idx)
        
        if outlier_indices:
            outlier_df = self.df_raw.loc[list(outlier_indices)].copy()
            outlier_df["异常原因"] = [outlier_reasons[idx] for idx in outlier_df.index]
            self.outlier_records = outlier_df
        else:
            self.outlier_records = None
    
    # 处理异常值
    def handle_outlier(self, mode="clip"):
        '''
            * 功能**：对数值列进行 IQR 异常检测与处理
            * **处理策略（mode 参数）**：
            * `"clip"`（推荐）：截断缩尾，超出上下限的值分别设为上限/下限值，**不丢失样本**
            * `"drop"`：删除包含异常值的整行，**谨慎使用**
            * **输出**：打印每列异常上下限、异常数量；返回处理后的 DataFrame
        '''
        self._build_outlier_records() # 构建异常值记录 DataFrame
        self.export_outlier_records() # 导出异常值记录到 CSV 文件
        for col in self._get_numeric_cols():
            lower, upper = self._calc_iqr_bounds(col)
            outlier_count = ((self.df[col] < lower) | (self.df[col] > upper)).sum()
            
            if mode == "clip":
                print(f"截断缩尾处理异常值的列：{col}")
                print(f"{col}列异常值上下限：[{lower:.2f}, {upper:.2f}]")
                print(f"{col}列一共处理 {outlier_count} 个异常值。")
                self.df[col] = self.df[col].clip(lower=lower, upper=upper)
                self.outlier_stats[col] = {"count": outlier_count, "strategy": "截断缩尾", "lower": lower, "upper": upper}
            else:
                print(f"删除包含异常值的整行的列：{col}")
                print(f"{col}列异常值上下限：[{lower:.2f}, {upper:.2f}]")
                original_count = len(self.df)
                self.df = self.df[(self.df[col] >= lower) & (self.df[col] <= upper)]
                deleted_count = original_count - len(self.df)
                print(f"{col}列一共删除 {deleted_count} 行异常值。")
                self.outlier_stats[col] = {"count": deleted_count, "strategy": "删除整行", "lower": lower, "upper": upper}
        
        return self.df         

    def _section_shape(self):
        '''
            生成数据规模变化报告
            :return: 包含数据规模变化信息的字符串列表
        '''
        lines = []
        lines.append("【1. 数据规模变化】")
        lines.append(f"原始数据：{self.original_shape[0]} 行 × {self.original_shape[1]} 列")
        lines.append(f"清洗后：{self.df.shape[0]} 行 × {self.df.shape[1]} 列")
        lines.append(f"行数变化：{self.df.shape[0] - self.original_shape[0]} 行")
        lines.append(f"列数变化：{self.df.shape[1] - self.original_shape[1]} 列")
        return lines
    
    def _section_deleted_cols(self):
        '''
            生成删除列报告
            :return: 包含删除列信息的字符串列表
        '''
        lines = ["【2. 删除的列】"]
        if self.deleted_cols:
            for col in self.deleted_cols:
                rate = self.df_raw[col].isnull().sum() / len(self.df_raw)
                lines.append(f"  - {col}（缺失率: {rate:.1%}）")
        else:
            lines.append("  无")
        return lines
    
    def _section_missing(self):
        '''
            生成缺失值处理报告
            :return: 包含缺失值处理信息的字符串列表
        '''
        lines = ["【3. 缺失值处理】"]
        for col in self.missing_stats:
            stat = self.missing_stats[col]
            lines.append(f"  - {col}：")
            if stat["after"] is None:
                lines.append(f"\t\t缺失率：{stat['before']:.1%}（该列已删除）")
            else:
                lines.append(f"\t\t缺失率变化：{stat['before']:.1%} → {stat['after']:.1%}")
            lines.append(f"\t\t处理策略：{stat['strategy']}")
        return lines
    
    def _section_outlier(self):
        '''
            生成异常值处理报告
            :return: 包含异常值处理信息的字符串列表
        '''
        lines = ["【4. 异常值处理】"]
        for col in self.outlier_stats:
            stat = self.outlier_stats[col]
            lines.append(f"  - {col}：")
            lines.append(f"      异常值数量：{stat['count']} 个")
            lines.append(f"      正常值范围：[{stat['lower']:.2f}, {stat['upper']:.2f}]")
            lines.append(f"      处理策略：{stat['strategy']}")
        return lines
    
    def _section_export(self):
        '''
            生成异常记录导出报告
            :return: 包含异常记录导出信息的字符串列表
        '''
        lines = ["【5. 异常记录导出】"]
        if self.outlier_records is not None:
            lines.append(f"  导出异常记录数：{len(self.outlier_records)} 条")
        else:
            lines.append("  无异常记录")
        return lines
    
    def _build_report_lines(self):
        '''
            构建清洗报告的字符串列表
            :return: 包含清洗报告所有部分的字符串列表
        '''
        lines = []
        lines.append("="*60)
        lines.append("数据清洗报告")
        lines.append("="*60)
        lines.append("")
        lines.extend(self._section_shape())
        lines.append("")
        lines.extend(self._section_deleted_cols())
        lines.append("")
        lines.extend(self._section_missing())
        lines.append("")
        lines.extend(self._section_outlier())
        lines.append("")
        lines.extend(self._section_export())
        lines.append("")
        lines.append("="*60)
        return lines
    
    def create_clean_report(self, save_path="code/auto_clean_project/clean_data/clean_report.txt"):
        '''
            生成清洗报告，包含：
            * 原始行数/列数 vs 清洗后行数/列数
            * 各字段缺失率变化
            * 各字段异常值数量及处理策略
            * 删除的列名列表
        '''
        report_lines = self._build_report_lines()
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"清洗报告已保存到 {save_path}")
    
    def run_full_clean(self):
        '''
            * 功能**：清洗流水线统一入口
            * **执行顺序**：先调用 `handle_missing_value`，再调用 `handle_outlier`
            * **输出**：返回最终清洗完成的 DataFrame
        '''
        # 先处理缺失值
        self.handle_missing_value()
        # 再处理异常值
        self.handle_outlier()
        # 生成清洗报告
        self.create_clean_report()
        # 存储清洗后的数据到csv中
        self.save() 
        return self.df

    # 导出异常值记录
    def export_outlier_records(self, save_path="code/auto_clean_project/clean_data/outlier_record.csv"):
        '''
            将识别到的异常数据单独导出为 CSV 文件，供业务人工复核
            异常数据在原始数据格式基础上额外增加"异常原因"列，说明每行被识别为异常的原因
        '''
        if self.outlier_records is not None and len(self.outlier_records) > 0:
            self.outlier_records.to_csv(save_path, index=False, encoding="utf-8-sig")
            print(f"异常数据记录已保存到 {save_path}，共 {len(self.outlier_records)} 条异常记录")
        else:
            print("未检测到异常数据，无需导出异常记录")

    # 保存清洗完成的 DataFrame
    def save(self, save_path="code/auto_clean_project/clean_data/clean_data.csv"):
        '''
            * 功能**：将清洗完成的 DataFrame 保存为 CSV 文件
            * **参数**：`save_path`（可选）：指定保存路径，默认值为 `"cleaned_data.csv"`
        '''
        self.df.to_csv(save_path, index=False)
        print(f"清洗完成的 DataFrame 已保存到 {save_path}")
if __name__ == "__main__":
    # 读取原始数据
    df = pd.read_csv("code/auto_clean_project/raw_data/customer_chat_raw.csv", encoding="utf-8-sig")
    print("原始数据预览")
    print(df.head(50))
    # 实例化自动清洗流水线对象
    acd = AutoCleanDecision(df)
    # 运行自动清洗流水线
    acd.run_full_clean()