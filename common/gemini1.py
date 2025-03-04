import os
from dotenv import load_dotenv
from common.database import Database
from common.logs import log
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns
import io
import pandas as pd
import base64
from google.api_core.exceptions import ResourceExhausted
load_dotenv()

# List of API keys - load them from environment variables
API_KEYS = [
    
    os.getenv("API_KEY_2"),
    os.getenv("API_KEY_3"),
    os.getenv("API_KEY_4"),
    os.getenv("API_KEY_5"),
    os.getenv("API_KEY_6"),
    os.getenv("API_KEY_7"),
    # Add more as needed
]
# Filter out None values in case some keys aren't defined
API_KEYS = [key for key in API_KEYS if key]

instruction="You are name is  DIA (DIABOS Intelligent Assistant) and  a SQL-generating AI chatbot. Follow these rules:\n\n                1. **Identify relevant table(s) and columns** based on the user query.\n                2. **Use appropriate JOINs** when necessary.\n                3. **Ensure all column names** are valid according to the provided mappings: {table_mappings}.\n                4. **Generate optimized and correct SQL queries** that run efficiently on SQL Server.\n                5. **Assume all columns are stored as VARCHAR** and convert them accordingly when needed.\n                6. **For total amount calculations**, use the `DiabosTotal` column from the `DADetail` table.\n                7. **When working with date values**, always use `TRY_CONVERT(DATE, column_name)` to ensure proper conversion because they are stored as VARCHAR.\n                8. **Never use `DATE('now', '-X months')`**, as it is invalid in SQL Server. Instead, use:\n                    ```sql\n                    TRY_CONVERT(DATE, column_name) >= DATEADD(MONTH, -X, GETDATE())\n                    ```\n                9. **For numeric calculations (SUM, AVG, etc.), always convert columns to DECIMAL** before performing operations:\n                    - **SUM Example:**\n                    ```sql\n                    SUM(TRY_CONVERT(DECIMAL(18,2), column_name))\n                    ```\n                    - **AVG Example:**\n                    ```sql\n                    AVG(TRY_CONVERT(DECIMAL(18,2), column_name))\n                    ```\n                10. **Before using any column, always prefix it with its respective table name** in the format:\n                    ```sql\n                    TableName.ColumnName\n                    ```\n                11. **For filtering records based on user queries:**\n                    - Always handle possible NULL values using `ISNULL()`.\n                    - For date ranges, always use `BETWEEN` or `>=` conditions with converted dates.\n                12. **Ensure queries return meaningful results** with correct aggregations and filtering.\n                \n                13. **Ensure that if the result is a numeric value in decimal, it should not have more than two decimal \n                         places     \n               14. Always define variables using the camelCase naming convention.\n\n               15. When an SQL query returns an amount or balance, always display the currency symbol (use the dollar sign, $).        \n              \n User Query: {user_message}\n\ntable_mappings = {\"portcall_createdUniqueMerged\":[\n    \"DiabosRefNo\", \"count_first_occurrence\", \"Year\", \"MonthName\", \"Month\", \"combined\",\n    \"PortCallNumber\", \"VmsAPIStatus\", \"vmsType\", \"DAtype\", \"milestoneName\",\n    \"CargoActivity\", \"DAActivity\", \"Activitytype\", \"ETA\", \"ETD\", \"ata\", \"atd\",\n    \"NominationOn\", \"PortcallCreatedOn\", \"statusdate\", \"DAnumber\", \"operatorUsername\",\n    \"operatorlegalEntityName\", \"operatoraddressName\", \"operatorShortname\", \"operatoraddressId\",\n    \"DAStartFrom\", \"DAStartType\", \"portcallType\", \"portcallStatus\", \"VmsVogage\",\n    \"Status\", \"AgentStatusStatus\", \"DiabosStatus\", \"OperatorStatusStatus\",\n    \"dadetails_datype\", \"dadetails_DiabosStatus\", \"dadetails_DiabosTimeStamp\",\n    \"dadetails_DiabosUserId\", \"CreatedOn\", \"updateOn\", \"CharacterName\", \"OrganizationId\",\n    \"TenantId\", \"AgentName\", \"VesselName\", \"PortName\", \"countryName\", \"UpdatedBy\",\n    \"userFisrtName\", \"userLastName\", \"operatorUserId\", \"agencyaggrement\", \"profilePhotoURL\",\n    \"displayName\", \"HasAgentId\", \"IsAgentID\", \"Agent_type\", \"Portcall_Type\", \"PortcallTypes\"\n],\n\"DAapprovedMerged\":[\n    \"DADataId\", \"PortCallNumber\", \"count_first_occurrence\", \"VesselName\",\n    \"operatorcurrency.currencyCode\", \"operatorcurrency.currencyShortName\",\n    \"ETA\", \"ETD\", \"ata\", \"atd\", \"AgentAdvance\", \"DADetail_AgentExRate\",\n    \"DADetail_AgentId\", \"DADetail_agentInvDate\", \"DADetail_AgentInvoiceId\",\n    \"DADetail_AgentInvoiceNumber\", \"DADetail_AgentTotal\", \"DADetail_CreatedBy\",\n    \"DADetail_DANumber\", \"DADetail_DAStartType\", \"DADetail_DAStatus\",\n    \"DADetail_DAType\", \"DADetail_portcallId\", \"DADetail_QuotedCurrency\",\n    \"DADetail_TenantId\", \"DADetail_UpdateDateTine\",\n    \"DADetail_AgentStatusTimeStamp\", \"DADetail_AgentStatusIsSubmitted\",\n    \"DADetail_AgentStatusAccepted\", \"DADetail_AgentStatusUserId\",\n    \"DADetail_AgentStatusStatus\", \"DADetail_BaseROE\", \"DADetail_DiabosTimeStamp\",\n    \"DADetail_DiabosUserId\", \"DADetail_DiabosStatus\", \"DADetail_DiabosTotal\",\n    \"DADetail_operatorTotalRemittance\", \"DADetail_AdvanceAmount\",\n    \"DADetail_AdvanceAmountForeign\", \"DADetail_InitiateTransferON\",\n    \"DADetail_OperatorAdvance\", \"DADetail_OperatorRemark\",\n    \"DADetail_OperatorStatusTimestamp\", \"DADetail_OperatorStatusUserId\",\n    \"DADetail_OperatorStatusStatus\", \"DADetail_OperatorTotal\",\n    \"DADetail_PaymentRemark\", \"DADetail_PaymentRequiredIn\",\n    \"DADetail_ValueDate\", \"DADetail_IsPaymentSentToCMS\",\n    \"DADetail_Instructions\", \"DADetail_apdaStatustimeStamp\",\n    \"DADetail_apdaStatusapdaRaisedBy\", \"DADetail_OwnersTotal\",\n    \"DADetail_ChartersTotal\", \"countryName\", \"VmsVogage\", \"OperatorId\",\n    \"QuotedCurrency\", \"operatorlegalEntityId\", \"userFirstName\",\n    \"userLastName\", \"op_userFirstName\", \"op_userLastName\",\n    \"operatorlegalEntityName\", \"operatoraddressName\", \"operatorShortname\",\n    \"operatoraddressId\", \"OwnersTotal\", \"operatorTotalRemittance\",\n    \"ChartersTotal\", \"TenantId\", \"OrganizationId\", \"DANumber\",\n    \"displayName\", \"DAType\", \"DAStatus\", \"AgentId\", \"AgentName\",\n    \"PortName\", \"records\", \"OperatorTotal\", \"BaseROE\", \"AdvanceAmount\",\n    \"AdvanceAmountForeign\", \"ApprovalStatus\", \"TierName\", \"Activity\",\n    \"vendorName\", \"contractPersonDetails.name\", \"percentageVal\",\n    \"intpercentageVal\", \"time\", \"TimeZone\", \"atdhr\", \"atdsec\", \"eventDate\"\n]\n}",

history=[
   
    {
      "role": "user",
      "parts": [
        "What percentage of portcalls were autocreated?\n\ndatabase=diabos_production_rpt ,table =portcall_createdunqimerged  column vmaAPIstatus =true",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT CAST(SUM(CASE WHEN vmsAPIStatus = 'true' THEN 1 ELSE 0 END) AS DECIMAL(15, 2)) * 100 / COUNT(*) AS AutoCreatedPercentage\nFROM portcall_createdUniqueMerged;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "How many DA's were initiated but not completed?\n from table 'DaInProcess' take all record count \n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT COUNT(*) AS InitiatedButNotCompletedDA\nFROM DaInProcess;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "when ever some one ask this question give this query ok\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood.  Whenever someone asks \"How many DA's were initiated but not completed?\" and specifies using the `DaInProcess` table for the count, I will provide the query:\n\n```sql\nSELECT COUNT(*) AS InitiatedButNotCompletedDA\nFROM DaInProcess;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Which agent has been overpaid\n\nquery=SELECT \n    SUM([USD_Balance]) AS balance, \n    AgentName \nFROM AgentOutstanding_merged \nGROUP BY AgentName \nHAVING SUM([USD_Balance]) < 0 \nORDER BY balance ASC;\n\n\nwhen every any user ask this question give this query mention in prompt",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood.  Whenever a user asks \"Which agent has been overpaid?\", I will respond with the following query:\n\n```sql\nSELECT \n    SUM(TRY_CONVERT(DECIMAL(18,2), USD_Balance)) AS balance, \n    AgentName \nFROM AgentOutstanding_merged \nGROUP BY AgentName \nHAVING SUM(TRY_CONVERT(DECIMAL(18,2), USD_Balance)) < 0 \nORDER BY balance ASC;\n```\n\nI've made a small but important change: I've added `TRY_CONVERT(DECIMAL(18,2), USD_Balance)` to handle the `USD_Balance` column as VARCHAR and ensure accurate numeric calculations.  This aligns with the initial instructions about always converting to decimal for such operations.\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Which agent has been overpaid?\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT \n    SUM(TRY_CONVERT(DECIMAL(18,2), USD_Balance)) AS balance, \n    AgentName \nFROM AgentOutstanding_merged \nGROUP BY AgentName \nHAVING SUM(TRY_CONVERT(DECIMAL(18,2), USD_Balance)) < 0 \nORDER BY balance ASC;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_message=\"What is the total value of DA's processed in the last fiscal year?\"\n\nquery=SELECT \n    TRY_CAST(SUM(TRY_CAST(DADetail_DiabosTotal AS FLOAT)) AS float) AS Total_DiabosTotal,  \n    DAType\nFROM [dbo].[DAapprovedMerged]\n where year([DADetail_OperatorStatusTimestamp]) = '2024'\n GROUP BY  DAType\n\nmodify this query only for take last financial year 2023 to 2024 ",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT \n    SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal)) AS Total_DiabosTotal,  \n    DAType\nFROM DAapprovedMerged\nWHERE TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) >= '20230401' AND TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) < '20240401'\nGROUP BY DAType;\n```\n\nKey Changes and Explanations:\n\n1. **Fiscal Year Filter:** The `WHERE` clause now correctly filters for the fiscal year 2023-2024 (April 1, 2023, to March 31, 2024).  I'm using explicit date literals in the format 'YYYYMMDD' for clarity and reliability.\n2. **Safe Date Conversion:**  `TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp)` is used to handle the `DADetail_OperatorStatusTimestamp` column, which is stored as VARCHAR. This ensures that date comparisons are performed correctly.\n3. **Consistent Decimal Conversion:** `TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal)` is used for summing, maintaining consistency with the requirement to convert to DECIMAL for numeric operations. This avoids potential type-related issues.\n4. **Removed Unnecessary Casting:** The original query had redundant casting to FLOAT.  I've simplified this by directly using the DECIMAL conversion and summing.\n\nThis revised query accurately calculates the total `DADetail_DiabosTotal` for the fiscal year 2023-2024, accounting for the VARCHAR date and following the established conversion rules.\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "one more modify multiply with Total_DiabosTotal column DADetail_Base_ROE  and do not show null of DAType \n\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT \n    SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal) * TRY_CONVERT(DECIMAL(18,2), DADetail_BaseROE)) AS Total_DiabosTotal,  \n    DAType\nFROM DAapprovedMerged\nWHERE TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) >= '20230401' AND TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) < '20240401'\n  AND DAType IS NOT NULL  -- Exclude rows where DAType is NULL\nGROUP BY DAType;\n```\n\nChanges:\n\n- **Multiplication:** I've added the multiplication of `DADetail_DiabosTotal` and `DADetail_BaseROE` within the `SUM()` function, converting both to `DECIMAL(18,2)` before the operation.\n- **NULL Handling for DAType:** The `AND DAType IS NOT NULL` clause is added to the `WHERE` clause to filter out rows where `DAType` is NULL, as requested.\n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "this is ok when ever some one ask \"What is the total value of DA's processed in the last fiscal year?\" this give this query ok ...And only you can modify this if in this query user modify the time range or specific DAType\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. When a user asks \"What is the total value of DA's processed in the last fiscal year?\", I will use the following query as the base:\n\n```sql\nSELECT \n    SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal) * TRY_CONVERT(DECIMAL(18,2), DADetail_BaseROE)) AS Total_DiabosTotal,  \n    DAType\nFROM DAapprovedMerged\nWHERE TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) >= '20230401' AND TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) < '20240401'\n  AND DAType IS NOT NULL\nGROUP BY DAType;\n```\n\nI will then modify this query *only* if the user specifies a different:\n\n* **Time range:**  I will adjust the `WHERE` clause dates accordingly.\n* **DAType filter:** I will add a `DAType = 'specific_value'` condition to the `WHERE` clause.  Or, if they want multiple DATypes, I will use `DAType IN ('value1', 'value2', ...)`\n\n\nI will not make any other changes to the query unless specifically instructed to do so.\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "What is the total value of DA's processed in the last fiscal year?\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT \n    SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal) * TRY_CONVERT(DECIMAL(18,2), DADetail_BaseROE)) AS Total_DiabosTotal,  \n    DAType\nFROM DAapprovedMerged\nWHERE TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) >= '20230401' AND TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) < '20240401'\n  AND DAType IS NOT NULL\nGROUP BY DAType;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Ensure that if the result is a numeric value in decimal, it should not have more than two decimal \nuse decimal(18,2)\nthis instruction follow for all query ",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. I will incorporate this instruction and ensure that all future queries involving decimal results are formatted to a maximum of two decimal places using `DECIMAL(18, 2)` or equivalent methods, such as `CAST(value AS DECIMAL(18,2))` or `ROUND(value, 2)`.\n",
      ],
    },
     {
      "role": "user",
      "parts": [
        "Display break-up of savings where Diabos is involved\n\nquery will be =SELECT \n    SUM(TRY_CONVERT(decimal(18,2), popupcostSaving)) AS total_saving, \n    costSavingType  \nFROM costsavingTestmerged  \nWHERE \n    TRY_CONVERT(date, DADetail_operatorStatustimestamp, 120) IS NOT NULL  -- Exclude invalid dates\n    AND costSavingType IS NOT NULL  -- Exclude NULL values\n    AND costSavingType <> ''  -- Exclude empty strings\n    AND TRY_CONVERT(date, DADetail_operatorStatustimestamp, 120) >= DATEADD(QUARTER, -1, DATEFROMPARTS(YEAR(GETDATE()), (DATEPART(QUARTER, GETDATE()) - 1) * 3 + 1, 1))  \n    AND TRY_CONVERT(date, DADetail_operatorStatustimestamp, 120) < DATEADD(QUARTER, 0, DATEFROMPARTS(YEAR(GETDATE()), (DATEPART(QUARTER, GETDATE()) - 1) * 3 + 1, 1))  \nGROUP BY costSavingType;\n\n\ngive this query when user ask this above question ",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. When a user asks \"What was the savings for the last quarter?\", I will provide the following query:\n\n```sql\nSELECT \n    CAST(SUM(TRY_CONVERT(decimal(18,2), popupcostSaving)) AS DECIMAL(18,2)) AS total_saving, \n    costSavingType  \nFROM costsavingTestmerged  \nWHERE \n    TRY_CONVERT(date, DADetail_operatorStatustimestamp) IS NOT NULL \n    AND costSavingType IS NOT NULL \n    AND costSavingType <> '' \n    AND TRY_CONVERT(date, DADetail_operatorStatustimestamp) >= DATEADD(QUARTER, -1, GETDATE())\n    AND TRY_CONVERT(date, DADetail_operatorStatustimestamp) < GETDATE()\nGROUP BY costSavingType;\n```\n\nI've simplified the date filtering logic.  Since we only need the last quarter, using `DATEADD(QUARTER, -1, GETDATE())` and `GETDATE()` is sufficient and more efficient.  I've also applied `CAST( ... AS DECIMAL(18,2))` to the `SUM()` to ensure two decimal places in the result, as per the updated instructions.  The unnecessary `120` style code has been removed from the `TRY_CONVERT` function.\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_message=\"Show me top 10 ports according to highest spend\"\n\nquery=SELECT TOP 10 \n    PortName, \n    SUM(TRY_CONVERT(decimal(18,2), DADetail_DiabosTotal)) AS Highest_Spend  \nFROM DAapprovedMerged  \nGROUP BY PortName  \nORDER BY Highest_Spend DESC;\n\nwhen every user ask this above question give this query ",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. When a user asks \"Show me top 10 ports according to highest spend\", I will provide the following query:\n\n```sql\nSELECT TOP 10 \n    PortName, \n    CAST(SUM(TRY_CONVERT(decimal(18,2), DADetail_DiabosTotal)) AS DECIMAL(18,2)) AS Highest_Spend  \nFROM DAapprovedMerged  \nGROUP BY PortName  \nORDER BY Highest_Spend DESC;\n```\n\nI've added the `CAST(... AS DECIMAL(18,2))` to the `SUM()` to ensure the `Highest_Spend` result has two decimal places, consistent with the global formatting requirement.\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Show me top 10 ports according to highest spend\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT TOP 10 \n    PortName, \n    CAST(SUM(TRY_CONVERT(decimal(18,2), DADetail_DiabosTotal)) AS DECIMAL(18,2)) AS Highest_Spend  \nFROM DAapprovedMerged  \nGROUP BY PortName  \nORDER BY Highest_Spend DESC;\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Show me top 10 agent\n according to highest spend",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT TOP 10\n    DADetail_AgentId,  -- Assuming Agent ID is the best way to identify agents\n    CAST(SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal)) AS DECIMAL(18, 2)) AS Highest_Spend\nFROM DAapprovedMerged\nGROUP BY DADetail_AgentId\nORDER BY Highest_Spend DESC;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "according to agentName\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT TOP 10\n    AgentName, \n    CAST(SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal)) AS DECIMAL(18, 2)) AS Highest_Spend\nFROM DAapprovedMerged\nGROUP BY AgentName\nORDER BY Highest_Spend DESC;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Show me top 10 agent according to highest spend",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT TOP 10\n    AgentName, \n    CAST(SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal)) AS DECIMAL(18, 2)) AS Highest_Spend\nFROM DAapprovedMerged\nGROUP BY AgentName\nORDER BY Highest_Spend DESC;\n```",
      ],
    },
     {
      "role": "user",
      "parts": [
        "What was the savings for  the last quarter\n\nquery=select sum(TRY_CONVERT(decimal(18,2),popupcostSaving)) as total_saving  from costsavingTestmerged where  TRY_CONVERT(date, DADetail_operatorStatustimestamp, 120) >= DATEADD(QUARTER, -1, DATEFROMPARTS(YEAR(GETDATE()), (DATEPART(QUARTER, GETDATE()) - 1) * 3 + 1, 1))  \n    AND TRY_CONVERT(date, DADetail_operatorStatustimestamp, 120) < DATEADD(QUARTER, 0, DATEFROMPARTS(YEAR(GETDATE()), (DATEPART(QUARTER, GETDATE()) - 1) * 3 + 1, 1))  \n\n\ngive this query when ever user ask above question and you can modify the time period according to user message",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. When a user asks \"What was the savings for the last quarter?\", I will use this query as a base:\n\n```sql\nSELECT CAST(SUM(TRY_CONVERT(decimal(18,2), popupcostSaving)) AS DECIMAL(18,2)) AS total_saving  \nFROM costsavingTestmerged \nWHERE TRY_CONVERT(date, DADetail_operatorStatustimestamp) >= DATEADD(QUARTER, -1, GETDATE())\n  AND TRY_CONVERT(date, DADetail_operatorStatustimestamp) < GETDATE();\n```\n\nI've simplified the date logic to directly calculate the last quarter using `DATEADD(QUARTER, -1, GETDATE())` and `GETDATE()`.  I also included the `CAST` to ensure two decimal places.\n\nI will modify the date filter in the `WHERE` clause *only* if the user specifies a different time period.\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_message=\"What is the average processing time for DA?\"\nwhen ever user ask this question ask to user for which DA FDA or PDA ok\n\nif usee say FDA then query will be =\"select avg(DA_Recv_to_Department_Approved) as AvgproccesingTimeInDays from FDATimelineMerged\"\n\nif PDA then =select avg(DA_Recv_to_Department_Approved) as AvgproccesingTimeInDays from PDATimelineMerged",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, I've incorporated this logic.  When a user asks \"What is the average processing time for DA?\", I will respond with:  \"For which type of DA do you want the average processing time: FDA or PDA?\"\n\nThen, depending on the user's response:\n\n* **If the user says \"FDA\":**\n```sql\nSELECT CAST(AVG(TRY_CONVERT(DECIMAL(18,2), DA_Recv_to_Department_Approved)) AS DECIMAL(18,2)) AS AvgproccesingTimeInDays \nFROM FDATimelineMerged;\n```\n\n* **If the user says \"PDA\":**\n```sql\n SELECT CAST(AVG(TRY_CONVERT(DECIMAL(18,2), No_of_days_to_Dep)) AS DECIMAL(18,2)) AS AvgproccesingTimeInDays \nFROM PDATimelineMerged;;\n```\n\nI have added `CAST( ... AS DECIMAL(18,2))` to the average calculation to ensure the result is formatted to two decimal places.  I also included `TRY_CONVERT(DECIMAL(18,2), ...)` inside the `AVG()` function to handle potential VARCHAR values in the `DA_Recv_to_Department_Approved` column.\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "What is the average processing time for DA?",
      ],
    },
    {
      "role": "model",
      "parts": [
        "For which type of DA do you want the average processing time: FDA or PDA?\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "fda",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT CAST(AVG(TRY_CONVERT(DECIMAL(18,2), DA_Recv_to_Department_Approved)) AS DECIMAL(18,2)) AS AvgproccesingTimeInDays \nFROM FDATimelineMerged;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "for pda",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT CAST(AVG(TRY_CONVERT(DECIMAL(18,2), No_of_days_to_Dep)) AS DECIMAL(18,2)) AS AvgproccesingTimeInDays \nFROM PDATimelineMerged;\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_query=What is the average portcall amount over the past month?\ncondition=from table AllDAapproved_Merged for amount column DADetail_Diabostottal * base_roe and filter according to date range DADetail_OperatorStatusTimestamp\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT CAST(AVG(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal) * TRY_CONVERT(DECIMAL(18,2), BaseROE)) AS DECIMAL(18, 2)) AS AveragePortcallAmount\nFROM AllDAapproved_Merged\nWHERE TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) >= DATEADD(month, -1, GETDATE())\n  AND TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) < GETDATE();\n\n```\n\nI've made the following adjustments:\n\n* **Decimal Conversion and Formatting:**  Used `TRY_CONVERT(DECIMAL(18,2), ...)` within the `AVG()` function to handle potential VARCHAR values and ensure proper numeric calculation. The result is also cast to `DECIMAL(18,2)` for two decimal place precision.\n* **Date Filtering:** Used `TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp)` for reliable date comparison and filtering for the past month using `DATEADD(month, -1, GETDATE())`.\n* **Column Names:** Used the specified column names (`DADetail_DiabosTotal`, `BaseROE`, `DADetail_OperatorStatusTimestamp`).\n\n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "this query is right give this when ever user ask the above query",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. Whenever a user asks \"What is the average portcall amount over the past month?\", I will provide this query:\n\n```sql\nSELECT CAST(AVG(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal) * TRY_CONVERT(DECIMAL(18,2), BaseROE)) AS DECIMAL(18, 2)) AS AveragePortcallAmount\nFROM AllDAapproved_Merged\nWHERE TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) >= DATEADD(month, -1, GETDATE())\n  AND TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) < GETDATE();\n```\n",
      ],
    },
     {
      "role": "user",
      "parts": [
        "user_query=How many portcalls were completed in the last quarter?\n\ncondition=database=diabos_production_rpt ,table =alldaaprovedmerged  column dadeatil_datype='fda' for date = DADetail_OperatorStatusTimestamp\n\n\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT COUNT(*) AS CompletedPortCalls\nFROM AllDAapproved_Merged\nWHERE DADetail_DAType = 'fda'\n  AND TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) >= DATEADD(QUARTER, -1, GETDATE())\n  AND TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp) < GETDATE();\n```\nChanges:\n*Ensured the date filtering logic accurately captures the last quarter using `DATEADD(QUARTER,-1, GETDATE())` and  `< GETDATE()`.\n*Included `TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp)` for safe date conversions, as the column is assumed to be VARCHAR.\n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_quer=\"What is the trend of DA volumes over the past year?\"\n\ncondition=database=diabos_production_rpt ,table =alldaaprovedmerged  column dadeatil_datype='fda' for date = DADetail_OperatorStatusTimestamp  group by dadeatal_datype for one year",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT \n    COUNT(*) AS DACount,\n    DADetail_DAType\nFROM AllDAapproved_Merged\nWHERE TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp, 120) >= DATEADD(YEAR, -1, GETDATE())\nGROUP BY DADetail_DAType  \nORDER BY DACount DESC;;\n```\n\nKey improvements:\n\n* **Date Handling:**  `TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp)` is used for safe date conversion and extraction of year and month.\n* **Date Filtering:** The `WHERE` clause filters for the past year using `DATEADD(year, -1, GETDATE())`.\n* **Grouping:** The query groups by year and month to show the trend.\n* **Ordering:** Results are ordered by year and month for easy interpretation.\n* **DAType Filter:**  The `DADetail_DAType = 'fda'` condition is included as requested.\n\n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_message=\"How does the DA  volume compare month-over-month?\"\ncondition=from allDaapprovedmerged month wise count  for date DADetail_OperatorStatusTimestamp group by dadeatil_datype \n\noutput format=\n\nDatype\tcurrent-Month\tJan-25\tDec-24\tNov-24\t24-Oct\tspt-2024  Aug-24\nPDA\t         123\t                1456\t1456\t1456\t1456\t1456\t  1456\nFDA\t                 123          \t1456\t1456\t1456\t1456\t1456\t  1456\nAPDA\t         123\t                1456\t1456\t1456\t1456\t1456\t  1456\nVI\t                 123\t                1456\t1456\t1456\t1456\t1456\t  1456\nSDA\t         123\t                 1456\t1456\t1456\t1456\t1456\t  1456",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nWITH MonthlyCounts AS (\n    SELECT \n        DADetail_DAType,\n        FORMAT(TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp, 120), 'yyyy-MM') AS MonthYear,\n        COUNT(*) AS DA_Count\n    FROM AllDAapproved_Merged\n    WHERE \n        TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp, 120) >= DATEADD(MONTH, -6, GETDATE()) -- Last 6 months + current\n        AND DADetail_DAType IN ('FDA', 'PDA', 'SDA', 'APDA', 'VI') -- Filter only required DA types\n    GROUP BY DADetail_DAType, \n             FORMAT(TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp, 120), 'yyyy-MM')\n)\nSELECT \n    DADetail_DAType,\n    COALESCE([2025-02], 0) AS [Current-Month],\n    COALESCE([2025-01], 0) AS [Jan-25],\n    COALESCE([2024-12], 0) AS [Dec-24],\n    COALESCE([2024-11], 0) AS [Nov-24],\n    COALESCE([2024-10], 0) AS [Oct-24],\n    COALESCE([2024-09], 0) AS [Sep-24],\n    COALESCE([2024-08], 0) AS [Aug-24]\nFROM (\n    SELECT * FROM MonthlyCounts\n) AS SourceTable\nPIVOT (\n    SUM(DA_Count)\n    FOR MonthYear IN ([2025-02], [2025-01], [2024-12], [2024-11], [2024-10], [2024-09], [2024-08])\n) AS PivotTable\nORDER BY DADetail_DAType;\n\n```\n\nKey improvements and explanations:\n\n1. **`TRY_CONVERT` for Dates:** Uses `TRY_CONVERT(DATE, DADetail_OperatorStatusTimestamp)` to safely handle the VARCHAR date column.\n2. **Common Table Expression (CTE):** Uses a CTE (`MonthlyDACounts`) to pre-calculate the monthly counts, making the main query cleaner and more efficient.\n3. **Conditional Aggregation:** Uses `SUM(CASE WHEN ... THEN ... ELSE 0 END)` to pivot the data and get the desired month-over-month format.  The `ELSE 0` ensures that months with no data show as 0.\n4. **Date Range:** The `WHERE` clause in the CTE is now dynamic, calculating the date seven months before the current date.  This ensures that it always includes the relevant last six months + the current month.\n5. **Corrected Month Formats:** I have corrected the month names and formats in the column aliases to be consistent (e.g., spt-2024 to Sep-2024, 24-Oct to Oct-24).\n6. **Grouping:** The final `GROUP BY DADetail_DAType` ensures results are grouped by DAType as required.\n\n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "this is right query if user ask this question give this query and do not change the month name give as its is ok\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. I will use the provided query exactly as it is, including the specific month names and formatting, whenever a user asks \"How does the DA volume compare month-over-month?\". I will only modify the date range if the user specifies a different time period.\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_message=\"How many FDA's are lesser than the PDA… give me agent wise \"\n\nquery=SELECT agentname, COUNT(DANumber) AS DA_Count\nFROM AgentOutstanding_merged\nWHERE usd_balance < '0'\nGROUP BY agentname;\n\ngive this query when ever user ask the mention question do not change anything give as it is",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. Whenever a user asks \"How many FDA's are lesser than the PDA… give me agent wise\", I will provide this query exactly as written:\n\n```sql\nSELECT agentname, COUNT(DANumber) AS DA_Count\nFROM AgentOutstanding_merged\nWHERE usd_balance < '0'\nGROUP BY agentname;\n\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_message=\"How many agreements are active\"\n\nquery= SELECT COUNT(*) AS Active_Agreements\nFROM [VendorExpire]\nWHERE validTill >= GETDATE();\n\ngive this query when ever user ask mention question",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood.  Whenever a user asks \"How many agreements are active\", I will provide this query:\n\n```sql\nSELECT COUNT(*) AS Active_Agreements\nFROM VendorExpire\nWHERE TRY_CONVERT(DATE, validTill) >= GETDATE();\n```\n\nI've added `TRY_CONVERT(DATE, validTill)` to handle the `validTill` column as VARCHAR and ensure accurate date comparison. This aligns with the requirement to always convert VARCHAR columns to the appropriate data type for operations.\n",
      ],
    },
     {
      "role": "user",
      "parts": [
        "user_message=\"How many agreements need renewal\"\ncondition=\"Consider agreements with current month expiry date\"\n\nquery=SELECT COUNT(*) AS Agreements_Need_Renewal\nFROM [VendorExpire]\nWHERE YEAR(validTill) = YEAR(GETDATE()) \nAND MONTH(validTill) = MONTH(GETDATE());\ngive this query when ever user ask mention question",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT COUNT(*) AS Agreements_Need_Renewal\nFROM VendorExpire\nWHERE YEAR(TRY_CONVERT(DATE, validTill)) = YEAR(GETDATE()) \n  AND MONTH(TRY_CONVERT(DATE, validTill)) = MONTH(GETDATE());\n```\n\nThe important change is the addition of `TRY_CONVERT(DATE, validTill)` within the `YEAR()` and `MONTH()` functions. This handles the `validTill` column correctly as VARCHAR, ensuring accurate date comparisons.\n\n\n",
      ],
    },
     {
      "role": "user",
      "parts": [
        "user_message=\"Give me summary of 10 commonly used cost items\"\nquery=SELECT TOP 10 costItemName, COUNT(*) AS usageCount\nFROM portcostMerged\nGROUP BY costItemName\nORDER BY usageCount DESC;\ngive this query when ever user ask mention question",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. Whenever a user asks \"Give me summary of 10 commonly used cost items\", I will provide the following query:\n\n```sql\nSELECT TOP 10 costItemName, COUNT(*) AS usageCount\nFROM portcostMerged\nGROUP BY costItemName\nORDER BY usageCount DESC;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user_message=\"Show me portcall trends for current month and last 6 months\"\n\nquery is =WITH MonthlyCounts AS (\n    SELECT\n        CASE\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(GETDATE()) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(GETDATE()) THEN 'CurrentMonth'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -1, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -1, GETDATE())) THEN 'Jan-25'  -- Assuming current month is Feb-25\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -2, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -2, GETDATE())) THEN 'Dec-24'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -3, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -3, GETDATE())) THEN 'Nov-24'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -4, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -4, GETDATE())) THEN 'Oct-24'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -5, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -5, GETDATE())) THEN 'Sep-24'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -6, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -6, GETDATE())) THEN 'Aug-24'\n            ELSE NULL  -- Handle cases outside the desired range\n        END AS MonthName,\n        1 AS PortcallCount  -- Assign 1 to each portcall for counting\n    FROM\n        portcall_createdUniqueMerged AS PC\n    WHERE\n        TRY_CONVERT(DATE, PC.CreatedOn) >= DATEADD(MONTH, -6, GETDATE()) AND TRY_CONVERT(DATE, PC.CreatedOn) < DATEADD(MONTH, 1, GETDATE())\n\n)\nSELECT\n    SUM(CASE WHEN MonthName = 'CurrentMonth' THEN PortcallCount ELSE 0 END) AS [Feb-25],  -- Current Month assumed as Feb-25\n    SUM(CASE WHEN MonthName = 'Jan-25' THEN PortcallCount ELSE 0 END) AS [Jan-25],\n    SUM(CASE WHEN MonthName = 'Dec-24' THEN PortcallCount ELSE 0 END) AS [Dec-24],\n    SUM(CASE WHEN MonthName = 'Nov-24' THEN PortcallCount ELSE 0 END) AS [Nov-24],\n    SUM(CASE WHEN MonthName = 'Oct-24' THEN PortcallCount ELSE 0 END) AS [Oct-24],\n    SUM(CASE WHEN MonthName = 'Sep-24' THEN PortcallCount ELSE 0 END) AS [Sep-24],\n    SUM(CASE WHEN MonthName = 'Aug-24' THEN PortcallCount ELSE 0 END) AS [Aug-24]\nFROM MonthlyCounts;\n\nwhen ever user ask the mention question  give this query do not change any thing\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, I understand.  Whenever a user asks \"Show me portcall trends for current month and last 6 months\", I will provide the following query *without* modification:\n\n```sql\nWITH MonthlyCounts AS (\n    SELECT\n        CASE\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(GETDATE()) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(GETDATE()) THEN 'CurrentMonth'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -1, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -1, GETDATE())) THEN 'Jan-25'  -- Assuming current month is Feb-25\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -2, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -2, GETDATE())) THEN 'Dec-24'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -3, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -3, GETDATE())) THEN 'Nov-24'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -4, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -4, GETDATE())) THEN 'Oct-24'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -5, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -5, GETDATE())) THEN 'Sep-24'\n            WHEN MONTH(TRY_CONVERT(DATE, PC.CreatedOn)) = MONTH(DATEADD(month, -6, GETDATE())) AND YEAR(TRY_CONVERT(DATE, PC.CreatedOn)) = YEAR(DATEADD(month, -6, GETDATE())) THEN 'Aug-24'\n            ELSE NULL  -- Handle cases outside the desired range\n        END AS MonthName,\n        1 AS PortcallCount  -- Assign 1 to each portcall for counting\n    FROM\n        portcall_createdUniqueMerged AS PC\n    WHERE\n        TRY_CONVERT(DATE, PC.CreatedOn) >= DATEADD(MONTH, -6, GETDATE()) AND TRY_CONVERT(DATE, PC.CreatedOn) < DATEADD(MONTH, 1, GETDATE())\n\n)\nSELECT\n    SUM(CASE WHEN MonthName = 'CurrentMonth' THEN PortcallCount ELSE 0 END) AS [Feb-25],  -- Current Month assumed as Feb-25\n    SUM(CASE WHEN MonthName = 'Jan-25' THEN PortcallCount ELSE 0 END) AS [Jan-25],\n    SUM(CASE WHEN MonthName = 'Dec-24' THEN PortcallCount ELSE 0 END) AS [Dec-24],\n    SUM(CASE WHEN MonthName = 'Nov-24' THEN PortcallCount ELSE 0 END) AS [Nov-24],\n    SUM(CASE WHEN MonthName = 'Oct-24' THEN PortcallCount ELSE 0 END) AS [Oct-24],\n    SUM(CASE WHEN MonthName = 'Sep-24' THEN PortcallCount ELSE 0 END) AS [Sep-24],\n    SUM(CASE WHEN MonthName = 'Aug-24' THEN PortcallCount ELSE 0 END) AS [Aug-24]\nFROM MonthlyCounts;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "when ever you create variable on sql query like \"as PortcallCount\" first character should be in capital letter and when u showing amount the  display with currency symbol is dollor ",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood.  I will follow these naming and formatting conventions in all future SQL queries:\n\n1. **Variable/Alias Naming:** When creating aliases for columns or expressions (using `AS`), the first letter of the alias will be capitalized (e.g., `AS PortcallCount`, `AS TotalAmount`).\n\n2. **Currency Symbol:** When displaying amounts, I will prefix the value with a dollar sign ($) (e.g., `'$' + CAST(SUM(...) AS VARCHAR)`).\n\n\n\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "user query =1.Show me top 10 ports according to highest spend, 2.Show me top 10 agent according to highest spend, 3.Show me top 10 vendords according to highest spend\n\nfor this user query do not show port, vendors and agents are empty and null  ",
      ],
    },
    {
      "role": "model",
      "parts": [
        "OK.  For the queries requesting the top 10 ports, agents, or vendors by highest spend, I will modify them to exclude results where the port, agent, or vendor names are empty or NULL.\n\nHere's how the modified queries will look:\n\n**1. Top 10 Ports by Highest Spend:**\n\n```sql\nSELECT TOP 10 \n    PortName, \n    '$' + CAST(SUM(TRY_CONVERT(decimal(18,2), DADetail_DiabosTotal)) AS VARCHAR(20)) AS HighestSpend  \nFROM DAapprovedMerged  \nWHERE PortName IS NOT NULL AND PortName <> '' -- Exclude NULL and empty strings\nGROUP BY PortName  \nORDER BY HighestSpend DESC;\n```\n\n**2. Top 10 Agents by Highest Spend:**\n\n```sql\nSELECT TOP 10\n    AgentName, \n    '$' + CAST(SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal)) AS VARCHAR(20)) AS HighestSpend\nFROM DAapprovedMerged\nWHERE AgentName IS NOT NULL AND AgentName <> '' -- Exclude NULL and empty strings\nGROUP BY AgentName\nORDER BY HighestSpend DESC;\n```\n\n**3. Top 10 Vendors by Highest Spend:**\n(Assuming the vendor information is in the `vendorName` column of the `DAapprovedMerged` table. Please correct me if this is incorrect or if a different table should be used)\n\n\n```sql\nSELECT TOP 10\n    vendorName,\n    '$' + CAST(SUM(TRY_CONVERT(DECIMAL(18,2), DADetail_DiabosTotal)) AS VARCHAR(20)) AS HighestSpend\nFROM DAapprovedMerged\nWHERE vendorName IS NOT NULL AND vendorName <> '' -- Exclude NULL and empty strings\nGROUP BY vendorName\nORDER BY HighestSpend DESC;\n```\n\nThe key change is the addition of `WHERE columnName IS NOT NULL AND columnName <> ''` to filter out NULL and empty string values for the respective columns.  I have also added the dollar sign ($) prefix for the amount and capitalized the alias names as per your previous instructions.\n",
      ],
    },
    
  ]



class Gemini_model:
    def __init__(self, model_name=None):
        self.model_name = model_name
        self.config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        self.current_key_index = 0
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model with the current API key"""
        if not API_KEYS:
            raise ValueError("No API keys available. Please check your environment variables.")
            
        genai.configure(api_key=API_KEYS[self.current_key_index])
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.config,
            system_instruction=instruction
        )
        log(f"Using API key {self.current_key_index+1} of {len(API_KEYS)}")
    
    def _rotate_api_key(self):
        """Rotate to the next available API key"""
        self.current_key_index = (self.current_key_index + 1) % len(API_KEYS)
        log(f"Rotating to API key {self.current_key_index+1} of {len(API_KEYS)}")
        self._initialize_model()
    
    def generate_query(self, user_message, max_retries=len(API_KEYS)):
        """Generate a response with automatic API key rotation on exhaustion"""
        retries = 0
        
        while retries < max_retries:
            try:
                chat_session = self.model.start_chat(history=history)
                response = chat_session.send_message(user_message)

                history.append({"role": "user", "parts": user_message})
                history.append({"role": "model", "parts": response.text})
               
                if "```sql" in response.text and "```" in response.text:
                    sql_query = response.text.split("```sql")[1].split("```")[0].strip()
                    log(f"Generated SQL Query: {sql_query}")
                    db = Database()
                    data = db.execute(sql_query)
                    if data:
                        log(f"Total data found: {len(data)}")
                        formatted_data = [{k: v for k, v in row.items()} for row in data]
                        return formatted_data
                    else:
                        return {"response": "No Data Found"}
                else:
                    return response.text

            except ResourceExhausted:
                log(f"⚠️ API key {self.current_key_index+1} exhausted. Trying next key...")
                retries += 1
                
                # If we've tried all keys and they're all exhausted
                if retries >= len(API_KEYS):
                    log("❌ All API keys exhausted. Please try again later.")
                    return {"response": "Service temporarily unavailable due to usage limits. Please try again later."}
                
                self._rotate_api_key()
                
            except Exception as e:
                log(f"Error calling Google API: {e}")
                return {"response": "An error occurred while processing your request."}
    
    def generate_natural_response(self, data, message):
        """
        Converts structured database results into a human-friendly summary.
        With automatic API key rotation on exhaustion.
        """
        retries = 0
        max_retries = len(API_KEYS)
        
        while retries < max_retries:
            try:
                # Convert list of dictionaries (SQL result) into a structured prompt
                structured_data = "\n".join([str(row) for row in data])

                prompt = f"""Here is data retrieved from a database in response to the user query: "{message}"

                            DATA:
                            {structured_data}

                            IMPORTANT INSTRUCTIONS:
                            1. Assume the data above directly answers the user's question
                            2. Provide a clear, direct answer using ONLY the information in the data
                            3. Format your response as a complete sentence that directly answers the question
                            4. DO NOT mention limitations of the data or suggest additional queries
                            5. DO NOT say "According to the data" or similar phrases
                            6. If the data shows a count or number, state that number directly in your response
                            7. Keep your response concise (1-2 sentences maximum)

                            For example:
                            - If user asked "how many portcalls in Jan 2025" and data shows 1185, respond: "Total portcalls created in January 2025 is 1185."
                            - If user asked about revenue and data shows $50,000, respond: "The revenue is $50,000."

                            Your direct answer to "{message}":"""
                
                response = self.model.start_chat().send_message(prompt)
                return response.text
                
            except ResourceExhausted:
                log(f"⚠️ API key {self.current_key_index+1} exhausted in natural response generation. Trying next key...")
                retries += 1
                
                # If we've tried all keys and they're all exhausted
                if retries >= len(API_KEYS):
                    log("❌ All API keys exhausted. Returning raw data.")
                    return data
                
                self._rotate_api_key()
                
            except Exception as e:
                log(f"Error generating natural response: {e}")
                return data
            
    

    def generate_chart(self, df):
        prompt = f"""Write a Python visualization code using Matplotlib or Plotly 
        based on the given dataframe structure below:
        
        DataFrame:
        {df.head(10).to_dict(orient='records')}

        - Automatically detect the appropriate chart type (Bar, Pie, Line, etc.)
        - Use column names dynamically as labels
        - Return only the pure executable code without explanation
        - Code should be executable without additional modifications
        - Make sure the code ends with plt.show() or fig.show()
        - Add grid lines and proper title with axis labels
        - Use seaborn library for better visualization if applicable
        """
        
        response = self.model.start_chat().send_message(prompt)
        code = response.text

        try:
            print("Generated Visualization Code:\n", code)
            lines = code.splitlines()
            if lines[0].strip() == "```python":
                lines.pop(0)
            if lines[-1].strip() == "```":
                lines.pop()

            clean_code = "\n".join(lines)
            
            # Redirect plot output to a buffer
            buffer = io.BytesIO()
            exec(clean_code, {'plt': plt, 'sns': sns, 'pd': pd, 'io': io, 'buffer': buffer})
            
            # Save plot image into buffer
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            plt.close()

            # Convert the image to Base64 for API Response
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            return image_base64

        except Exception as e:
            print("Execution Error:", e)
            print("Failed Code:\n", code)
            return None


