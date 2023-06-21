from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["ecommerces"]

# Collection names
USERS_COLLECTION = 'users'
PRODUCTS_COLLECTION = 'products'


def add_user(user_id, purchased_products):
    users_collection = db[USERS_COLLECTION]
    user = {
        'user_id': user_id,
        'purchased_products': purchased_products
    }
    users_collection.insert_one(user)
    print(f"User '{user_id}' added successfully.")


def add_product(product_id, product_name):
    products_collection = db[PRODUCTS_COLLECTION]
    product = {
        'product_id': product_id,
        'product_name': product_name
    }
    products_collection.insert_one(product)
    print(f"Product '{product_id}' added successfully.")


def recommend_products(user_id, num_recommendations):
    users_collection = db[USERS_COLLECTION]
    products_collection = db[PRODUCTS_COLLECTION]

    # Retrieve the user's purchased products from the "users" collection
    user = users_collection.find_one({'user_id': user_id})
    if not user:
        print(f"User '{user_id}' not found.")
        return []

    purchased_products = user['purchased_products']

    # Find users who have purchased similar products
    similar_users = users_collection.find({'purchased_products': {'$in': purchased_products}})

    # Get the list of purchased products from similar users
    similar_users_products = []
    for similar_user in similar_users:
        similar_users_products.extend(similar_user['purchased_products'])

    # Find frequently purchased products by similar users
    frequently_purchased_products = products_collection.aggregate([
        {'$match': {'product_id': {'$nin': purchased_products}}},
        {'$unwind': '$product_id'},
        {'$group': {'_id': '$product_id', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': num_recommendations}
    ])

    recommended_products = [product['_id'] for product in frequently_purchased_products]
    return recommended_products


# Menu-driven program
while True:
    print("----------------------------------------------")
    print("====== Recommendation System Menu ======")
    print("----------------------------------------------")
    print("1. Add User")
    print("2. Add Product")
    print("3. Recommend Products")
    print("4. Exit")
    print("-----------------------------------------------")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        user_id = input("Enter user ID: ")
        purchased_products = input("Enter purchased products (comma-separated): ").split(',')
        add_user(user_id, purchased_products)
    elif choice == '2':
        product_id = input("Enter product ID: ")
        product_name = input("Enter product name: ")
        add_product(product_id, product_name)
    elif choice == '3':
        user_id = input("Enter user ID: ")
        num_recommendations = int(input("Enter the number of recommendations: "))
        recommendations = recommend_products(user_id, num_recommendations)
        print(f"Recommended products for user '{user_id}': {recommendations}")
    elif choice == '4':
        print("Exiting the program...")
        break
    else:
        print("Invalid choice. Please try again.")

# Close the MongoDB connection
client.close()
