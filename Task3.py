import pandas as pd
import logging

import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
import os
load_dotenv()
class DisputeAnalyzer:
    def __init__(self):
        self.df_combined = None
        self.llm = None
        self.load_data()
        self.setup_llm()

    def load_data(self):
        disputes = pd.read_csv("disputes.csv")
        transactions = pd.read_csv("transactions.csv")
        classified = pd.read_csv("classified_disputes.csv")
        resolutions = pd.read_csv("resolutions.csv")

        disputes['created_at'] = pd.to_datetime(disputes['created_at'])
        transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])

        merged = pd.merge(disputes, transactions, on=['txn_id', 'customer_id'], how='left',
                          suffixes=('_dispute', '_txn'))

        merged = pd.merge(merged, classified, on='dispute_id', how='left')

        self.df_combined = pd.merge(merged, resolutions, on='dispute_id', how='left')

        logger.info(f"Data loaded successfully. Combined dataset has {len(self.df_combined)} rows")
        logger.info(f"Columns: {list(self.df_combined.columns)}")

    def setup_llm(self):
        # set your own api_key and base url (OpenAI) in os env
        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                base_url=os.getenv('OPENAI_BASE_URL')
            )
            logger.info("OpenAI client configured successfully")

        except Exception as e:
            logger.error(f"Error setting up OpenAI: {e}")
            self.client = None
    def create_system_prompt(self):

        # Get data schema information
        schema_info = {
            'columns': list(self.df_combined.columns),
            'categories': list(self.df_combined[
                                   'predicted_category'].unique()) if 'predicted_category' in self.df_combined.columns else [],
            'actions': list(self.df_combined[
                                'suggested_action'].unique()) if 'suggested_action' in self.df_combined.columns else [],
            'date_columns': ['created_at', 'timestamp']
        }

        prompt = f"""You are a pandas query generator for dispute analysis. Generate ONLY the pandas code, no explanations.

Available DataFrame: df_combined
Columns: {schema_info['columns']}

Categories: {schema_info['categories']}
Suggested Actions: {schema_info['actions']}
Date columns: {schema_info['date_columns']}

Rules:
1. Always use df_combined as the DataFrame name
2. For date filters, use pd.Timestamp() or datetime operations
3. For "today" use: df_combined['created_at'].dt.date == pd.Timestamp.now().date()
4. For counting: len(df_combined[condition]) or df_combined[condition].shape[0]
5. For filtering by category: df_combined['predicted_category'] == 'CATEGORY_NAME'
6. For unresolved disputes: df_combined['suggested_action'] != 'Auto-refund'
7. For grouping/breakdown: df_combined.groupby('column').size() or .value_counts()
8. Use case-sensitive exact matches for categories and actions

Query Examples:
- "How many duplicate charges today?" → len(df_combined[(df_combined['predicted_category'] == 'DUPLICATE_CHARGE') & (df_combined['created_at'].dt.date == pd.Timestamp.now().date())])
- "List unresolved fraud disputes" → df_combined[(df_combined['predicted_category'] == 'FRAUD') & (df_combined['suggested_action'] != 'Auto-refund')]

Generate pandas code for this query:"""

        return prompt

    def generate_pandas_query(self, user_query):
        if self.client is None:
            logger.error("OpenAI client not initialized")
            return "df_combined.head()"

        try:
            system_prompt = self.create_system_prompt()

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,
                max_tokens=150
            )

            generated_code = response.choices[0].message.content.strip()
            logger.info(f"Generated code: {generated_code}")

            pandas_code = self.extract_pandas_code(generated_code, "")
            if not pandas_code or pandas_code == "df_combined.head()":
                raise ValueError("Failed to generate valid pandas code")

            return pandas_code

        except Exception as e:
            logger.error(f"Error in query generation: {e}")
            return "df_combined.head()"

    def extract_pandas_code(self, generated_text, original_prompt):
        try:
            code_part = generated_text.replace(original_prompt, "").strip()

            # Remove arrows and example prefixes
            code_part = re.sub(r'^.*?→\s*', '', code_part, flags=re.MULTILINE)
            code_part = re.sub(r'^.*?:\s*', '', code_part, flags=re.MULTILINE)

            lines = code_part.split('\n')
            pandas_lines = []

            for line in lines:
                line = line.strip()
                if line and (
                        'df_combined' in line
                        or line.startswith('len(')
                        or line.startswith('pd.')
                ):
                    line = line.strip("'\"")
                    pandas_lines.append(line)

            code = " ".join(pandas_lines)  # join into one string
            return code if code else "df_combined.head()"

        except Exception as e:
            logger.error(f"Error extracting pandas code: {e}")
            return "df_combined.head()"

    def execute_query(self, pandas_code):
        try:
            safe_globals = {
                'df_combined': self.df_combined,
                'pd': pd,
                'len': len,
                '__builtins__': {}
            }

            # Execute the code
            result = eval(pandas_code, safe_globals)
            logger.info(f"Query executed successfully: {pandas_code}")
            return result, None

        except Exception as e:
            error_msg = f"Error executing query '{pandas_code}': {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    def process_query(self, user_query):
        """Main method to process user query and return results"""
        logger.info(f"Processing query: {user_query}")

        # Generate pandas code
        pandas_code = self.generate_pandas_query(user_query)

        # Execute query
        result, error = self.execute_query(pandas_code)

        return {
            'user_query': user_query,
            'generated_code': pandas_code,
            'result': result,
            'error': error,
            'success': error is None
        }

if __name__ == "__main__":
    analyzer = DisputeAnalyzer()
    test_queries = [
        "How many duplicate charges on 2nd august 2025?",
        "List unresolved fraud disputes",
        "Break down disputes by type",
        "Count all disputes",
        "Show fraud disputes"
    ]

    for query in test_queries:
        print(f"\n{'=' * 50}")
        print(f"Query: {query}")
        print(f"{'=' * 50}")

        response = analyzer.process_query(query)

        print(f"Generated Code: {response['generated_code']}")
        if response['success']:
            print(f"Result: {response['result']}")
        else:
            print(f"Error: {response['error']}")
