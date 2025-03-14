import sqlite3
from datetime import datetime

conn = sqlite3.connect('lib.sl3')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        copies INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS borrowings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        borrow_date TEXT,
        return_date TEXT,
        returned INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )
''')

conn.commit()

def add_book():
    title = input("Введите название книги: ")
    author = input("Введите автора: ")
    year = int(input("Введите год издания: "))
    copies = int(input("Введите количество экземпляров: "))
    cursor.execute("INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)", 
                   (title, author, year, copies))
    conn.commit()
    print("Книга добавлена!")

def register_user():
    first_name = input("Введите имя: ")
    last_name = input("Введите фамилию: ")
    email = input("Введите email: ")
    try:
        cursor.execute("INSERT INTO users (first_name, last_name, email) VALUES (?, ?, ?)", 
                       (first_name, last_name, email))
        conn.commit()
        print("Пользователь зарегистрирован!")
    except sqlite3.IntegrityError:
        print("Ошибка: Этот email уже зарегистрирован!")

def issue_book():
    user_id = int(input("Введите ID пользователя: "))
    book_id = int(input("Введите ID книги: "))
    
    cursor.execute("SELECT copies FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    if not book:
        print("Книга не найдена!")
        return
    
    if book[0] <= 0:
        print("Нет доступных экземпляров!")
        return
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        print("Пользователь не найден!")
        return
    
    borrow_date = datetime.now().strftime("%Y-%m-%d")
    # Устанавливаем фиксированный срок возврата (например, через 14 дней вручную)
    return_date = datetime.strptime(borrow_date, "%Y-%m-%d")
    return_date = (return_date.replace(day=return_date.day + 14)).strftime("%Y-%m-%d")
    
    cursor.execute("INSERT INTO borrowings (user_id, book_id, borrow_date, return_date, returned) VALUES (?, ?, ?, ?, 0)", 
                   (user_id, book_id, borrow_date, return_date))
    cursor.execute("UPDATE books SET copies = copies - 1 WHERE id = ?", (book_id,))
    conn.commit()
    print(f"Книга выдана! Срок возврата: {return_date}")

def return_book():
    borrowing_id = int(input("Введите ID записи о выдаче: "))
    
    cursor.execute("SELECT book_id, returned FROM borrowings WHERE id = ? AND returned = 0", (borrowing_id,))
    borrowing = cursor.fetchone()
    if not borrowing:
        print("Запись не найдена или книга уже возвращена!")
        return
    
    cursor.execute("UPDATE borrowings SET returned = 1 WHERE id = ?", (borrowing_id,))
    cursor.execute("UPDATE books SET copies = copies + 1 WHERE id = ?", (borrowing[0],))
    conn.commit()
    print("Книга возвращена!")

def view_available_books():
    cursor.execute("SELECT * FROM books WHERE copies > 0")
    books = cursor.fetchall()
    if not books:
        print("Нет доступных книг!")
        return
    for book in books:
        print(f"ID: {book[0]}, Название: {book[1]}, Автор: {book[2]}, Год: {book[3]}, Экземпляров: {book[4]}")

def view_borrowing_history():
    cursor.execute('''
        SELECT b.id, u.first_name, u.last_name, b.title, bo.borrow_date, bo.return_date, bo.returned
        FROM borrowings bo
        JOIN users u ON bo.user_id = u.id
        JOIN books b ON bo.book_id = b.id
    ''')
    history = cursor.fetchall()
    if not history:
        print("История выдачи пуста!")
        return
    for record in history:
        status = "Возвращена" if record[6] == 1 else "Не возвращена"
        print(f"ID записи: {record[0]}, Пользователь: {record[1]} {record[2]}, Книга: {record[3]}, "
              f"Дата выдачи: {record[4]}, Срок возврата: {record[5]}, Статус: {status}")

def main():
    while True:
        print("\n1. Добавить книгу")
        print("2. Зарегистрировать пользователя")
        print("3. Выдать книгу")
        print("4. Вернуть книгу")
        print("5. Показать доступные книги")
        print("6. Показать историю выдачи")
        print("7. Выход")
        
        choice = input("Выберите действие (1-7): ")
        
        if choice == '1':
            add_book()
        elif choice == '2':
            register_user()
        elif choice == '3':
            issue_book()
        elif choice == '4':
            return_book()
        elif choice == '5':
            view_available_books()
        elif choice == '6':
            view_borrowing_history()
        elif choice == '7':
            break
        else:
            print("Неверный выбор!")

    conn.close()

if __name__ == "__main__":
    main()
