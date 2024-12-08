import psycopg2
from psycopg2.extras import RealDictCursor

#ibsheets credentials
DB_HOST = "34.41.134.112"
DB_PORT = 5432
DB_NAME = "ibsheets"
DB_USER = "postgres"
DB_PASSWORD = "IBeasy395m"

def check_deal_exists(target, buyer):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        #checks for matching deal
        query = """
        SELECT *
        FROM deals
        WHERE LOWER(target) = LOWER(%s)
          AND LOWER(buyer) = LOWER(%s);
        """
        cursor.execute(query, (target, buyer))

        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"error querying database: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    target = input("enter target company: ").strip()
    buyer = input("enter buyer company: ").strip()

    #checks if deal exists
    deal_exists = check_deal_exists(target, buyer)
    if deal_exists:
        print("deal exists")
    else:
        print("deal does not exist")

if __name__ == "__main__":
    main()
