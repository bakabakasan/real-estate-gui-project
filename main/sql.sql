-- CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL);

--CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, phone_number TEXT, email TEXT, message TEXT, page_url TEXT);

--CREATE TABLE IF NOT EXISTS estate (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, location TEXT, cost REAL, currency TEXT, bedroom TEXT, description TEXT, additional_information TEXT, area TEXT, floor TEXT);

--INSERT INTO estate (type, location, cost, currency, bedroom, description, additional_information, area, floor)
--VALUES ('Квартира', 'Минск, Беларусь', 90000, 'USD', 2, 'Квартира с отличной планировкой, с мебелью и бытовой техникой, полностью готова к проживанию. Есть телефон, охранная сигнализация. Три окна с видом на парк.', 'Возможно оформить в кредит.', '53 кв.м.', '3 этаж');            
          
--INSERT INTO estate (type, location, cost, currency, bedroom, description, area, floor)
--VALUES ('Квартира', 'Гродно, Беларусь', 30000, 'USD', 1, 'Уютная квартира в Гродно, в районе с развитой структурой. Рядом Вокзал и торговые центры, и остановки общественного транспорта.', '32 кв.м.', '2 этаж');            
         
--INSERT INTO estate (type, location, cost, currency, bedroom, description, additional_information, area, floor)
--VALUES ('Дом', 'Витебск, Беларусь', NULL, 'USD', 3, 'Двухэтажный коттедж с гаражом на две машины. Участок 18 соток. Подведены все коммуникации к дому. Сделана разводка всех коммуникаций по дому.', 'Возможна оплата в кредит.', '125 кв.м.', '2 этажа');           

--INSERT INTO estate (type, location, cost, currency, bedroom, description, area, floor)
--VALUES ('Дом', 'Полоцк, Беларусь', 100000, 'USD', 4, 'Дом расположен в живописном районе с развитой инфраструктурой. В районе имеется школа, сад, конный клуб, почта и продуктовые магазины.', '96 кв.м.', '1 этаж');            
            