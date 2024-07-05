cursor = mydb.cursor()
sql_insert_query = """INSERT INTO test (public_key, private_key) VALUES (%s, %s)"""
record_to_insert = (encrypted_result,decrypted_result)

# Step 2: Execute the INSERT statement
cursor.execute(sql_insert_query, record_to_insert)

# Step 3: Commit the transaction
mydb.commit()

# Step 4: Close the cursor and connection
cursor.close()
mydb.close()