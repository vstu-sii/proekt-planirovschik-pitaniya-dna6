@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User

rectangle "AI Планировщик питания" {
  
  usecase "Настроить профиль" as UC1
  usecase "Пополнить базу\n«Мои продукты»" as UC2
  usecase "Сгенерировать\nменю" as UC3
  usecase "Заменить блюдо" as UC4
  usecase "Перенести блюдо" as UC5
  usecase "Сгенерировать рецепт\nиз остатков" as UC6
  usecase "Сгенерировать\nбыстрый ужин" as UC7
}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC1
User --> UC2
User --> UC3
User --> UC4
User --> UC5
User --> UC6
User --> UC7

@enduml