# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# # Assuming you already have `df`
# # Example: print(df.head())

# # Identify column types

# class Charts:
#     def __init__(self,df):
#         self.df=df
#         self.categorical_cols = self.df.select_dtypes(include=["object"]).columns.tolist()
#         self.numeric_cols = self.df.select_dtypes(include=["int", "float"]).columns.tolist()

#     def plot_dynamic_charts(self):
#         plt.figure(figsize=(15, 8))

#         # Bar Chart (Categorical vs Numeric)
#         if self.categorical_cols and self.numeric_cols:
#             plt.subplot(2, 2, 1)
#             sns.barplot(x= self.df[self.categorical_cols[0]], y= self.df[self.numeric_cols[0]], data= self.df, palette="viridis")
#             plt.title(f"Bar Chart: {self.categorical_cols[0]} vs {self.numeric_cols[0]}")

#         # Line Chart (Trend over first numeric column)
#         if self.numeric_cols:
#             plt.subplot(2, 2, 2)
#             self.df_sorted =  self.df.sort_values(by=self.numeric_cols[0])
#             sns.lineplot(x=range(len( self.df_sorted)), y= self.df_sorted[self.numeric_cols[0]], marker="o")
#             plt.title(f"Line Chart: Trend of {self.numeric_cols[0]}")

#         # Scatter Plot (First two numeric columns)
#         if len(self.numeric_cols) > 1:
#             plt.subplot(2, 2, 3)
#             sns.scatterplot(x= self.df[self.numeric_cols[0]], y= self.df[self.numeric_cols[1]], hue= self.df[self.categorical_cols[0]], palette="coolwarm")
#             plt.title(f"Scatter Plot: {self.numeric_cols[0]} vs {self.numeric_cols[1]}")

#         # Heatmap (Correlation of numeric columns)
#         if len(self.numeric_cols) > 1:
#             plt.subplot(2, 2, 4)
#             sns.heatmap( self.df[self.numeric_cols].corr(), annot=True, cmap="coolwarm", linewidths=0.5)
#             plt.title("Heatmap: Correlation Matrix")

#         plt.tight_layout()
#         plt.show()



def charts(message):
    chart = False
    chart_type = None
    
    chart_keywords = {
        'pie': ['pie', 'donut'],
        'bar': ['bar', 'histogram'],
        'line': ['line', 'trends'],
        'graph': ['graph', 'plot']
    }

    message_words = message.lower().split(" ")
    
    for word in message_words:
        for c_type, keywords in chart_keywords.items():
            if word in keywords:
                chart = True
                chart_type = c_type
                return chart, chart_type  # Return as soon as a chart type is found
    
    return chart, chart_type         

   
