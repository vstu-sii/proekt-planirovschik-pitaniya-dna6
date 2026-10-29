@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "БД профилей" as ProfileDB

rectangle "AI Планировщик питания" {
  
  usecase "UC-1. Настроить профиль" as UC1

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC1

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ
' UC-1: Настройка профиля
UC1 ..> ProfileDB : <<include>>\nСохранить ограничения

@enduml