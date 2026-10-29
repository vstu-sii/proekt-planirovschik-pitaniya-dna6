@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "RAG «Продукты и цены»" as RAG
actor "CV Модель" as CV

rectangle "AI Планировщик питания" {

  usecase "UC-8. Рассчитать КБЖУ\nпо фото" as UC8

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC8

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-8: Оценка КБЖУ по фото
UC8 ..> CV : <<include>>\nПроанализировать изображение
UC8 ..> RAG : <<include>>\nПосчитать цены и КБЖУ

@enduml