from scripts.fetch_data import get_transactions

def fetch_wallet_data(wallet: str):
    try:
        transactions = get_transactions(wallet)

        # Debug logs
        print("TYPE:", type(transactions))
        print("SAMPLE:", transactions[:2] if transactions else "No data")

        #Correct format
        if not isinstance(transactions, list):
            raise ValueError("Transactions should be a list")

        return transactions

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []