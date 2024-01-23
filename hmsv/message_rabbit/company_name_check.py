import psycopg2
import os
import dotenv

dotenv.load_dotenv()

def check(company_code):
    conn = psycopg2.connect(
        host = 'host.docker.internal',
        dbname = os.getenv('POSTGRES_DB'),
        user = os.getenv('POSTGRES_USER'),
        password = os.getenv('POSTGRES_PASSWORD'),
        port = os.getenv('POSTGRES_PORT')
    )
    cursor = conn.cursor()

    sql = f"select * from company where code = '{company_code}';"

    cursor.execute(sql)
    result = cursor.fetchone()
    # print(result)

    if result == None:  ## 새로운 Company일 경우
        insert_sql = f"INSERT INTO company(code_name) VALUES ('{company_code}') ;"
        cursor.execute(insert_sql)
        conn.commit()
        print("Data Save")

        cursor.execute(sql)
        result = cursor.fetchone()

    cursor.close()
    conn.close()

    return int(result[0]) # type: ignore


if __name__ == "__main__":

    check('A')