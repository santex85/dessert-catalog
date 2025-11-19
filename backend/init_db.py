"""
Script for initializing the database with test data
"""
from app.database import SessionLocal, engine, Base
from app.models import Dessert, User
from app.auth import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

# Test data - various desserts with different categories
sample_desserts = [
    {
        "title": "New York Cheesecake",
        "category": "Cakes",
        "image_url": "/static/images/cheesecake.jpg",
        "description": "Classic cheesecake with a delicate creamy taste and crispy cookie base. Perfect for special occasions.",
        "ingredients": "Cream cheese, sugar, eggs, cream, cookies, butter, vanilla",
        "calories": 321.5,
        "proteins": 5.2,
        "fats": 22.1,
        "carbs": 25.8,
        "weight": "800g",
        "is_active": True
    },
    {
        "title": "Tiramisu",
        "category": "Desserts",
        "image_url": "/static/images/tiramisu.jpg",
        "description": "Italian dessert with coffee, mascarpone and cocoa. Delicate and airy, with a rich coffee aroma.",
        "ingredients": "Mascarpone, sugar, eggs, espresso coffee, savoiardi, cocoa powder, cognac",
        "calories": 287.3,
        "proteins": 6.1,
        "fats": 18.5,
        "carbs": 24.2,
        "weight": "600g",
        "is_active": True
    },
    {
        "title": "Red Velvet Cake",
        "category": "Cakes",
        "image_url": "/static/images/red-velvet.jpg",
        "description": "Bright cake with chocolate flavor and cream cheese. Visually impressive dessert for holidays.",
        "ingredients": "Flour, sugar, cocoa, eggs, vegetable oil, buttermilk, cream cheese, food coloring",
        "calories": 345.2,
        "proteins": 4.8,
        "fats": 19.3,
        "carbs": 38.7,
        "weight": "1200g",
        "is_active": True
    },
    {
        "title": "Chocolate Eclair",
        "category": "Pastries",
        "image_url": "/static/images/eclair.jpg",
        "description": "Classic French pastry with delicate custard cream and chocolate glaze.",
        "ingredients": "Flour, eggs, milk, sugar, butter, chocolate, vanilla",
        "calories": 298.6,
        "proteins": 5.5,
        "fats": 16.2,
        "carbs": 32.1,
        "weight": "80g",
        "is_active": True
    },
    {
        "title": "Vegan Brownie",
        "category": "Vegan",
        "image_url": "/static/images/brownie.jpg",
        "description": "Chocolate brownie without eggs and dairy products. Rich taste and texture, suitable for vegans.",
        "ingredients": "Flour, cocoa, sugar, vegetable oil, banana, nuts, baking powder",
        "calories": 312.4,
        "proteins": 4.2,
        "fats": 15.8,
        "carbs": 42.3,
        "weight": "400g",
        "is_active": True
    },
    {
        "title": "Sugar-Free Cake",
        "category": "Sugar-Free",
        "image_url": "/static/images/sugar-free.jpg",
        "description": "Diet cake based on stevia and fruits. Suitable for diabetics and health-conscious people.",
        "ingredients": "Flour, stevia, eggs, vegetable oil, apples, cinnamon, walnuts",
        "calories": 198.7,
        "proteins": 6.1,
        "fats": 8.5,
        "carbs": 24.2,
        "weight": "900g",
        "is_active": True
    },
    {
        "title": "Strawberry Shortcake",
        "category": "Cakes",
        "image_url": "/static/images/shortcake.jpg",
        "description": "Light and airy cake with fresh strawberries and whipped cream. Perfect summer dessert.",
        "ingredients": "Flour, sugar, eggs, butter, strawberries, cream, vanilla extract",
        "calories": 275.3,
        "proteins": 4.5,
        "fats": 14.2,
        "carbs": 32.8,
        "weight": "1000g",
        "is_active": True
    },
    {
        "title": "Chocolate Chip Cookies",
        "category": "Cookies",
        "image_url": "/static/images/cookies.jpg",
        "description": "Classic homemade cookies with chocolate chips. Crispy on the outside, soft on the inside.",
        "ingredients": "Flour, butter, sugar, eggs, chocolate chips, vanilla, baking soda",
        "calories": 485.2,
        "proteins": 5.8,
        "fats": 24.3,
        "carbs": 62.1,
        "weight": "500g (12 pieces)",
        "is_active": True
    },
    {
        "title": "Lemon Tart",
        "category": "Tarts",
        "image_url": "/static/images/lemon-tart.jpg",
        "description": "Tangy lemon curd in a buttery shortcrust pastry. Refreshing and elegant dessert.",
        "ingredients": "Flour, butter, sugar, eggs, lemons, cream, vanilla",
        "calories": 312.6,
        "proteins": 5.1,
        "fats": 18.7,
        "carbs": 35.4,
        "weight": "600g",
        "is_active": True
    },
    {
        "title": "Macarons Assortment",
        "category": "Pastries",
        "image_url": "/static/images/macarons.jpg",
        "description": "French macarons in various flavors: vanilla, chocolate, raspberry, pistachio. Delicate and colorful.",
        "ingredients": "Almond flour, sugar, egg whites, food coloring, ganache, jam",
        "calories": 412.8,
        "proteins": 6.2,
        "fats": 19.5,
        "carbs": 52.3,
        "weight": "300g (12 pieces)",
        "is_active": True
    },
    {
        "title": "Carrot Cake",
        "category": "Cakes",
        "image_url": "/static/images/carrot-cake.jpg",
        "description": "Moist cake with grated carrots, spices, and cream cheese frosting. Healthy and delicious.",
        "ingredients": "Flour, carrots, sugar, eggs, vegetable oil, cinnamon, walnuts, cream cheese",
        "calories": 298.4,
        "proteins": 5.3,
        "fats": 16.8,
        "carbs": 34.2,
        "weight": "1100g",
        "is_active": True
    },
    {
        "title": "Panna Cotta",
        "category": "Desserts",
        "image_url": "/static/images/panna-cotta.jpg",
        "description": "Italian dessert made with sweetened cream and gelatin. Served with berry sauce.",
        "ingredients": "Cream, sugar, gelatin, vanilla, berries, honey",
        "calories": 256.7,
        "proteins": 3.8,
        "fats": 18.2,
        "carbs": 22.1,
        "weight": "200g",
        "is_active": True
    },
    {
        "title": "Apple Pie",
        "category": "Pies",
        "image_url": "/static/images/apple-pie.jpg",
        "description": "Classic American pie with spiced apple filling and flaky crust. Best served warm.",
        "ingredients": "Flour, butter, apples, sugar, cinnamon, nutmeg, lemon juice",
        "calories": 267.5,
        "proteins": 3.2,
        "fats": 12.4,
        "carbs": 38.6,
        "weight": "800g",
        "is_active": True
    },
    {
        "title": "Chocolate Mousse",
        "category": "Desserts",
        "image_url": "/static/images/mousse.jpg",
        "description": "Light and airy chocolate mousse with rich cocoa flavor. Topped with fresh berries.",
        "ingredients": "Dark chocolate, eggs, sugar, cream, vanilla, berries",
        "calories": 342.1,
        "proteins": 5.6,
        "fats": 24.3,
        "carbs": 28.4,
        "weight": "250g",
        "is_active": True
    },
    {
        "title": "Creme Brulee",
        "category": "Desserts",
        "image_url": "/static/images/creme-brulee.jpg",
        "description": "Classic French dessert with rich custard base and caramelized sugar top. Elegant and sophisticated.",
        "ingredients": "Cream, egg yolks, sugar, vanilla, caramel",
        "calories": 298.3,
        "proteins": 4.2,
        "fats": 20.1,
        "carbs": 24.8,
        "weight": "180g",
        "is_active": True
    },
    {
        "title": "Gluten-Free Chocolate Cake",
        "category": "Gluten-Free",
        "image_url": "/static/images/gluten-free.jpg",
        "description": "Rich chocolate cake made with almond flour. Suitable for those with gluten intolerance.",
        "ingredients": "Almond flour, cocoa, sugar, eggs, butter, chocolate, vanilla",
        "calories": 328.5,
        "proteins": 7.2,
        "fats": 22.4,
        "carbs": 28.6,
        "weight": "700g",
        "is_active": True
    },
    {
        "title": "Fruit Tart",
        "category": "Tarts",
        "image_url": "/static/images/fruit-tart.jpg",
        "description": "Beautiful tart with pastry cream and fresh seasonal fruits. Colorful and refreshing.",
        "ingredients": "Flour, butter, eggs, cream, sugar, fresh fruits (strawberries, kiwi, blueberries)",
        "calories": 245.8,
        "proteins": 4.1,
        "fats": 14.3,
        "carbs": 28.2,
        "weight": "650g",
        "is_active": True
    },
    {
        "title": "Banana Bread",
        "category": "Breads",
        "image_url": "/static/images/banana-bread.jpg",
        "description": "Moist and flavorful banana bread with walnuts. Perfect for breakfast or snack.",
        "ingredients": "Flour, bananas, sugar, eggs, butter, walnuts, cinnamon, baking soda",
        "calories": 312.4,
        "proteins": 5.8,
        "fats": 12.6,
        "carbs": 48.2,
        "weight": "600g",
        "is_active": True
    },
    {
        "title": "Pecan Pie",
        "category": "Pies",
        "image_url": "/static/images/pecan-pie.jpg",
        "description": "Rich and sweet pie with pecans in a caramel-like filling. Traditional Southern dessert.",
        "ingredients": "Flour, butter, pecans, corn syrup, sugar, eggs, vanilla, salt",
        "calories": 456.2,
        "proteins": 6.3,
        "fats": 28.4,
        "carbs": 48.7,
        "weight": "750g",
        "is_active": True
    },
    {
        "title": "Ice Cream Sundae",
        "category": "Ice Cream",
        "image_url": "/static/images/sundae.jpg",
        "description": "Vanilla ice cream with hot fudge, whipped cream, and cherry on top. Classic treat.",
        "ingredients": "Vanilla ice cream, chocolate fudge, whipped cream, cherry, nuts",
        "calories": 342.6,
        "proteins": 4.8,
        "fats": 18.5,
        "carbs": 42.3,
        "weight": "300g",
        "is_active": True
    }
]

def init_db():
    db = SessionLocal()
    try:
        desserts_count = 0
        users_count = 0
        
        # Check and add test desserts
        if db.query(Dessert).count() == 0:
            for dessert_data in sample_desserts:
                dessert = Dessert(**dessert_data)
                db.add(dessert)
            desserts_count = len(sample_desserts)
        
        # Check and create test administrator
        if db.query(User).filter(User.username == "admin").count() == 0:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            users_count = 1
            print("✓ Created test administrator:")
            print("  Username: admin")
            print("  Password: admin123")
        
        # Create test regular user
        if db.query(User).filter(User.username == "user").count() == 0:
            user = User(
                username="user",
                email="user@example.com",
                hashed_password=get_password_hash("user123"),
                is_admin=False,
                is_active=True
            )
            db.add(user)
            users_count += 1
            print("✓ Created test user:")
            print("  Username: user")
            print("  Password: user123")
        
        db.commit()
        
        if desserts_count > 0:
            print(f"✓ Successfully added {desserts_count} desserts to the database.")
        if users_count > 0:
            print(f"✓ Created {users_count} test users.")
        
        if desserts_count == 0 and users_count == 0:
            print("Database already contains data. Skipping initialization.")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

