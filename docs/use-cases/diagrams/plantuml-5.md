@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "RAG «Продукты и цены»" as RAG

rectangle "AI Планировщик питания" {
  
  usecase "UC-5. Перенести блюдо" as UC5

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC5

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-5: Каскадный перенос меню
UC5 ..> RAG : <<include>>\nПосчитать цены и КБЖУ

@enduml