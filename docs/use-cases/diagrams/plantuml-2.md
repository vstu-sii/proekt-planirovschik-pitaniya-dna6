@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "RAG «Продукты и цены»" as RAG
actor "БД «Мои продукты»" as LocalDB

rectangle "AI Планировщик питания" {
  
  usecase "UC-2. Пополнить базу\n«Мои продукты»" as UC2

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC2

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-2: Пополнение локальной базы «Мои продукты»
UC2 ..> RAG : <<include>>\nПолучить срок годности
UC2 ..> LocalDB : <<include>>\nСохранить в локальную БД

@enduml