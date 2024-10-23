
import random
import sqlite3


class Account:
    def __init__(self):
        self.lista_account = []
        self.lista_pin = []
        self.conn = sqlite3.connect('card.s3db')
        self.c = self.conn.cursor()
        self.create_table()
        self.main_menu()
        print('\nBye!')
        self.conn.close()

    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS card(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0);
        ''')
        self.conn.commit()

    def calculate_luhn(self, card_list):
        for x in range(len(card_list)):
            card_list[x] = int(card_list[x])
        luhn_numbers = []
        sumatorio = 0
        for i in range(len(card_list)):
            if i % 2 == 0:
                odd = card_list[i] * 2
                if odd > 9:
                    odd -= 9
                luhn_numbers.append(odd)
            else:
                if card_list[i] > 9:
                    card_list[i] -= 9
                luhn_numbers.append(card_list[i])

        for number in luhn_numbers:
            sumatorio += number
        if sumatorio % 10 == 0:
            checksum = 0
        else:
            checksum = (int(sumatorio / 10) * 10 + 10) - sumatorio
        return checksum

    def check_luhn(self, card):
        lista_card = list(card)
        last_digit = int(lista_card.pop(len(lista_card)-1))
        ultimo_digito = self.calculate_luhn(lista_card)
        if ultimo_digito == last_digit:
            return 0
        else:
            return 1

    def create_account(self):
        inn = str(random.randint(400000000000000, 400000999999999))
        card_list = list(inn)
        checksum = self.calculate_luhn(card_list)
        final_account = inn + str(checksum)
        pin_code = str.zfill(str(random.randint(0000, 9999)), 4)
        print(f'\nYour card has been created\nYour card number:\n{final_account}\nYour card PIN:\n{pin_code}\n')
        self.create_card(final_account, pin_code, 0)

    def create_card(self, number, pin, balance):
        sql_insert_card = 'INSERT INTO card (number, pin, balance) VALUES (?, ?, ?);'
        tupla = (number, pin, balance)
        self.c.execute(sql_insert_card, tupla)
        self.conn.commit()

    def log_account(self):
        enter_number = input('\nEnter your card number:\n')
        enter_pin = input('Enter your PIN:\n')
        self.c.execute(f'SELECT * FROM card WHERE number={enter_number} and pin={enter_pin}')
        if bool(self.c.fetchone()) is not False:
            print('\nYou have successfully logged in!\n')
            self.menu_balance(enter_number)
        else:
            print('Wrong card number or PIN!\n')

    def check_number(self, card):
        self.c.execute(f'SELECT id FROM card WHERE number={card}')
        if bool(self.c.fetchone()) is not False:
            return 0
        else:
            return 1

    def cerrar_programa(self):
        print('\nBye!')
        exit()

    def main_menu(self):
        option_inicio = '1'
        while option_inicio != '0':
            print('1.Create an account\n2. Log into account\n0. Exit')
            option_inicio = input()

            if option_inicio == '1':
                self.create_account()
            elif option_inicio == '2':
                self.log_account()
            elif option_inicio == '0':
                self.cerrar_programa()
            else:
                print(f'{option_inicio} is not a correct option')

    def update_balance(self, card, new_balance):
        self.c.execute(f'UPDATE card SET balance = {new_balance} WHERE number = {card};')
        self.conn.commit()

    def check_balance(self, card):
        self.c.execute(f'SELECT balance FROM card WHERE number=({card});')
        balance_amount = self.c.fetchone()
        return balance_amount[0]
    
    def make_transfer(self, card, transfer_card):
        amount_transfer = int(input('Enter how much money you want to transfer:\n'))
        self.c.execute(f'SELECT balance FROM card WHERE number = {card}')
        sql_balance = self.c.fetchone()
        if amount_transfer > sql_balance[0]:
            print('Not enough money!')
        else:
            rest = sql_balance[0] - amount_transfer
            self.update_balance(card, rest)
            self.update_balance(transfer_card, amount_transfer)
            print('Success!')

    def delete_account(self, card):
        self.c.execute(f'DELETE FROM card WHERE number={card}')
        self.conn.commit()

    def menu_balance(self, card):
        option = 1
        while option != 0:
            option = int(input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5.Log out\n0.Exit\n'))

            if option == 1:
                balance = self.check_balance(card)
                print(f'\nBalance: {balance}\n')
            elif option == 2:
                income = int(input('Enter income:\n'))
                balance = self.check_balance(card)
                final_balance = income + balance
                self.update_balance(card,final_balance)
                print(f'\nIncome was added!\n')

            elif option == 3:
                transfer_card = input('\nTransfer\nEnter card number:\n')
                result_luhn = self.check_luhn(transfer_card)
                check_number = self.check_number(transfer_card)
                if card == transfer_card:
                    print("You can't transfer money to the same account!")
                elif result_luhn == 1:
                    print('Probably you made a mistake in the card number. Please try again!')
                elif check_number == 1:
                    print('Such a card does not exist')
                else:
                    self.make_transfer(card,transfer_card)
            elif option == 4:
                self.delete_account(card)
                print('The account has been closed!')
                self.main_menu()
            elif option == 5:
                print('You have successfully logged out!\n')
                self.main_menu()
            elif option == 0:
                self.cerrar_programa()


if __name__ == '__main__':
    createAccount = Account()
