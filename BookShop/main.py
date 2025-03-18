import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


# Определение модели Publisher
class Publisher(Base):
    __tablename__ = 'publishers'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=100), unique=True)

    # Связь с книгами
    books = relationship("Book", back_populates="publisher")


# Определение модели Shop
class Shop(Base):
    __tablename__ = 'shops'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=100), unique=True)

    # Связь со складами
    stocks = relationship("Stock", back_populates="shop")


# Определение модели Book
class Book(Base):
    __tablename__ = 'books'

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=200), nullable=False)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey('publishers.id'), nullable=False)

    # Связь с издателем
    publisher = relationship("Publisher", back_populates="books")
    # Связь со складами
    stocks = relationship("Stock", back_populates="book")


# Определение модели Stock
class Stock(Base):
    __tablename__ = 'stocks'

    id = sq.Column(sq.Integer, primary_key=True)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey('shops.id'), nullable=False)
    id_book = sq.Column(sq.Integer, sq.ForeignKey('books.id'), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)  # Добавлено поле count

    # Связь с магазином и книгой
    shop = relationship("Shop", back_populates="stocks")
    book = relationship("Book", back_populates="stocks")


# Определение модели Sale
class Sale(Base):
    __tablename__ = 'sales'

    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.Float, nullable=False)
    date_sale = sq.Column(sq.DateTime, default=datetime.utcnow)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey('stocks.id'), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)

    # Связь с складом
    stock = relationship("Stock")


def create_tables(engine):
    # Удаление существующих таблиц
    Base.metadata.drop_all(engine)
    # Создание новых таблиц
    Base.metadata.create_all(engine)


# Параметры подключения
DSN = "postgresql://postgres:aeg19802402@localhost:5432/bookshop"
engine = sqlalchemy.create_engine(DSN)

try:
    create_tables(engine)

    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()

    # Пример создания объектов
    publisher1 = Publisher(name="Пушкин")
    book1 = Book(title="Капитанская дочка", publisher=publisher1)
    book2 = Book(title="Руслан и Людмила", publisher=publisher1)
    book3 = Book(title="Евгений Онегин", publisher=publisher1)

    shop1 = Shop(name="Буквоед")
    shop2 = Shop(name="Лабиринт")
    shop3 = Shop(name="Книжный дом")

    # Добавим книги и магазины в сессию
    session.add_all([publisher1, book1, book2, book3, shop1, shop2, shop3])
    session.commit()

    # Создание объектов Stock и Sale
    stock1 = Stock(shop=shop1, book=book1, count=10)
    stock2 = Stock(shop=shop1, book=book2, count=5)
    stock3 = Stock(shop=shop2, book=book1, count=3)
    stock4 = Stock(shop=shop3, book=book3, count=7)

    session.add_all([stock1, stock2, stock3, stock4])
    session.commit()

    # Добавление продаж
    sale1 = Sale(price=600, id_stock=1, count=1, date_sale=datetime.strptime('2022-11-09', '%Y-%m-%d'))
    sale2 = Sale(price=500, id_stock=2, count=1, date_sale=datetime.strptime('2022-11-08', '%Y-%m-%d'))
    sale3 = Sale(price=600, id_stock=1, count=1, date_sale=datetime.strptime('2022-10-26', '%Y-%m-%d'))
    sale4 = Sale(price=580, id_stock=3, count=1, date_sale=datetime.strptime('2022-11-05', '%Y-%m-%d'))
    sale5 = Sale(price=490, id_stock=4, count=1, date_sale=datetime.strptime('2022-11-02', '%Y-%m-%d'))

    session.add_all([sale1, sale2, sale3, sale4, sale5])
    session.commit()


    # Функция получения магазинов и продаж
    def get_shops(user_input):
        query = session.query(
            Book.title,
            Shop.name,
            Sale.price,
            Sale.date_sale
        ).select_from(Shop) \
            .join(Stock).join(Book).join(Sale)

        if user_input.isdigit():  # Если введен ID
            results = query.filter(Publisher.id == int(user_input)).all()
        else:  # Если введено имя
            results = query.join(Publisher).filter(Publisher.name == user_input).all()

        for title, shop_name, price, date in results:
            print(f"{title: <40} | {shop_name: <15} | {price: <8} | {date.strftime('%d-%m-%Y')}")


    if __name__ == '__main__':
        user_input = input("Введите ID или имя публициста: ")  # Запрос ввода от пользователя
        get_shops(user_input)  # Вызов функции

except Exception as e:
    print(f"Произошла ошибка: {e}")
    session.rollback()  # Откат в случае ошибки
finally:
    session.close()  # Закрытие сессии
