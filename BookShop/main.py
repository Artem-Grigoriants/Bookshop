from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker


# Функция для получения информации о базе данных от пользователя
def get_database_config():
    db_user = input("Введите имя пользователя базы данных: ")
    db_password = input("Введите пароль базы данных: ")
    db_host = input("Введите хост базы данных (например, localhost): ")
    db_port = input("Введите порт базы данных (например, 5432): ")
    db_name = input("Введите имя базы данных: ")
    return db_user, db_password, db_host, db_port, db_name


# Получаем параметры подключения к базе данных
db_user, db_password, db_host, db_port, db_name = get_database_config()

# Создание подключения к базе данных
DATABASE_URL = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(DATABASE_URL)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

# Получение имени или идентификатора издателя от пользователя
publisher_input = input("Введите имя или идентификатор издателя: ")

# Проверка, является ли входное значение числом (идентификатором)
if publisher_input.isdigit():
    publisher_id = int(publisher_input)
    publisher = session.query(Publisher).filter(Publisher.id == publisher_id).first()
else:
    publisher_name = publisher_input
    publisher = session.query(Publisher).filter(Publisher.name.ilike(f"%{publisher_name}%")).first()

# Если издатель найден
if publisher:
    print(f"Издатель: {publisher.name} (ID: {publisher.id})")

    # Получение магазинов, продающих книги этого издателя
    results = session.query(Shop).join(Stock).join(Book).filter(Book.id_publisher == publisher.id).all()

    if results:
        print("Магазины, продающие книги этого издателя:")
        for shop in results:
            print(f"- {shop.name} (ID: {shop.id})")
    else:
        print("Нет магазинов, продающих книги этого издателя.")
else:
    print("Издатель не найден.")

# Закрытие сессии
session.close()