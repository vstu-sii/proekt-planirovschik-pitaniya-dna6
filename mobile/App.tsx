import { StatusBar } from 'expo-status-bar'
import { useState } from 'react'
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native'

type Screen = 'profile' | 'pantry' | 'plan'

const screens: Screen[] = ['profile', 'pantry', 'plan']

function initialScreen(): Screen {
  if (typeof window === 'undefined') return 'profile'
  const requested = new URLSearchParams(window.location.search).get('screen')
  return screens.includes(requested as Screen)
    ? (requested as Screen)
    : 'profile'
}

const meals = [
  {
    type: 'Завтрак',
    name: 'Овсянка с яблоком',
    kcal: '420 ккал',
    time: '10 мин',
  },
  { type: 'Обед', name: 'Гречка с курицей', kcal: '680 ккал', time: '25 мин' },
  {
    type: 'Ужин',
    name: 'Тёплый салат с фасолью',
    kcal: '510 ккал',
    time: '20 мин',
  },
]

function Header({
  step,
  title,
  subtitle,
}: {
  step: string
  title: string
  subtitle: string
}) {
  return (
    <View style={styles.header}>
      <Text style={styles.brand}>ЕДА · ПРОСТО</Text>
      <Text style={styles.step}>{step}</Text>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.subtitle}>{subtitle}</Text>
    </View>
  )
}

function Field({
  label,
  value,
  suffix,
}: {
  label: string
  value: string
  suffix?: string
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.inputRow}>
        <TextInput editable={false} style={styles.input} value={value} />
        {suffix && <Text style={styles.suffix}>{suffix}</Text>}
      </View>
    </View>
  )
}

function Chip({
  children,
  active = false,
}: {
  children: string
  active?: boolean
}) {
  return (
    <View style={[styles.chip, active && styles.chipActive]}>
      <Text style={[styles.chipText, active && styles.chipTextActive]}>
        {children}
      </Text>
    </View>
  )
}

function PrimaryButton({
  title,
  onPress,
}: {
  title: string
  onPress: () => void
}) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={styles.button}
    >
      <Text style={styles.buttonText}>{title}</Text>
    </Pressable>
  )
}

function ProfileScreen({ next }: { next: () => void }) {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Header
        step="Шаг 1 из 2"
        title="Настроим рацион под вас"
        subtitle="Данные нужны, чтобы рассчитать бюджет и ориентиры КБЖУ."
      />
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Основные параметры</Text>
        <View style={styles.columns}>
          <Field label="Рост" value="178" suffix="см" />
          <Field label="Вес" value="74" suffix="кг" />
        </View>
        <Field label="Бюджет на неделю" value="3 500" suffix="₽" />
        <Text style={styles.label}>Цель</Text>
        <View style={styles.chips}>
          <Chip>Снизить вес</Chip>
          <Chip active>Поддерживать</Chip>
          <Chip>Набрать вес</Chip>
        </View>
        <Text style={styles.label}>Сколько готовить одно блюдо</Text>
        <View style={styles.chips}>
          <Chip>до 15 мин</Chip>
          <Chip active>до 30 мин</Chip>
          <Chip>не важно</Chip>
        </View>
      </View>
      <PrimaryButton title="Продолжить" onPress={next} />
      <Text style={styles.privacy}>
        Ваши данные используются только для составления плана
      </Text>
    </ScrollView>
  )
}

function PantryScreen({ next }: { next: () => void }) {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Header
        step="Шаг 2 из 2"
        title="Что уже есть дома?"
        subtitle="Учтём запасы, чтобы покупать меньше и не выбрасывать продукты."
      />
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Ваши продукты</Text>
        {[
          ['Гречка', '450 г'],
          ['Яйца', '6 шт'],
          ['Фасоль консервированная', '1 банка'],
        ].map(([name, amount]) => (
          <View key={name} style={styles.productRow}>
            <View style={styles.productIcon}>
              <Text>✓</Text>
            </View>
            <View style={styles.productText}>
              <Text style={styles.productName}>{name}</Text>
              <Text style={styles.productAmount}>{amount}</Text>
            </View>
            <Text style={styles.remove}>×</Text>
          </View>
        ))}
        <View style={styles.addProduct}>
          <Text style={styles.addProductText}>＋ Добавить продукт</Text>
        </View>
      </View>
      <View style={styles.notice}>
        <Text style={styles.noticeTitle}>Ограничения</Text>
        <Text style={styles.noticeText}>Без арахиса · Не люблю сельдерей</Text>
      </View>
      <PrimaryButton title="Составить план" onPress={next} />
      <Text style={styles.privacy}>
        Обычно генерация занимает меньше минуты
      </Text>
    </ScrollView>
  )
}

function PlanScreen() {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Header
        step="План готов"
        title="Понедельник"
        subtitle="Рацион укладывается в бюджет и использует продукты из ваших запасов."
      />
      <View style={styles.summary}>
        <View>
          <Text style={styles.summaryValue}>1 610</Text>
          <Text style={styles.summaryLabel}>ккал</Text>
        </View>
        <View>
          <Text style={styles.summaryValue}>108 г</Text>
          <Text style={styles.summaryLabel}>белок</Text>
        </View>
        <View>
          <Text style={styles.summaryValue}>487 ₽</Text>
          <Text style={styles.summaryLabel}>стоимость</Text>
        </View>
      </View>
      {meals.map((meal, index) => (
        <View key={meal.name} style={styles.mealCard}>
          <View
            style={[styles.mealNumber, index === 1 && styles.mealNumberAccent]}
          >
            <Text style={styles.mealNumberText}>{index + 1}</Text>
          </View>
          <View style={styles.mealBody}>
            <Text style={styles.mealType}>{meal.type}</Text>
            <Text style={styles.mealName}>{meal.name}</Text>
            <Text style={styles.mealMeta}>
              {meal.kcal} · {meal.time}
            </Text>
          </View>
          <Text style={styles.chevron}>›</Text>
        </View>
      ))}
      <View style={styles.budgetCard}>
        <View>
          <Text style={styles.noticeTitle}>Бюджет недели</Text>
          <Text style={styles.noticeText}>Осталось 91 ₽ из 3 500 ₽</Text>
        </View>
        <Text style={styles.budgetOk}>✓</Text>
      </View>
      <PrimaryButton title="Открыть список покупок" onPress={() => undefined} />
    </ScrollView>
  )
}

export default function App() {
  const [screen, setScreen] = useState<Screen>(initialScreen)
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View style={styles.phone}>
        {screen === 'profile' && (
          <ProfileScreen next={() => setScreen('pantry')} />
        )}
        {screen === 'pantry' && <PantryScreen next={() => setScreen('plan')} />}
        {screen === 'plan' && <PlanScreen />}
        <View style={styles.prototypeNav}>
          {screens.map((item) => (
            <Pressable
              key={item}
              onPress={() => setScreen(item)}
              style={styles.navDot}
            >
              <View style={[styles.dot, screen === item && styles.dotActive]} />
            </Pressable>
          ))}
        </View>
      </View>
    </SafeAreaView>
  )
}

const colors = {
  ink: '#172019',
  muted: '#68756b',
  green: '#246b45',
  pale: '#eef5ef',
  line: '#dce5dd',
  cream: '#f7f5ef',
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.cream },
  phone: {
    flex: 1,
    width: '100%',
    maxWidth: 480,
    alignSelf: 'center',
    backgroundColor: colors.cream,
  },
  content: { padding: 24, paddingBottom: 88 },
  header: { marginTop: 10, marginBottom: 22 },
  brand: {
    color: colors.green,
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 1.5,
  },
  step: { marginTop: 30, color: colors.green, fontSize: 13, fontWeight: '700' },
  title: {
    marginTop: 8,
    color: colors.ink,
    fontSize: 36,
    fontWeight: '800',
    lineHeight: 40,
  },
  subtitle: {
    marginTop: 12,
    color: colors.muted,
    fontSize: 16,
    lineHeight: 24,
  },
  card: {
    padding: 20,
    borderRadius: 22,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: colors.line,
  },
  sectionTitle: {
    marginBottom: 18,
    color: colors.ink,
    fontSize: 18,
    fontWeight: '800',
  },
  columns: { flexDirection: 'row', gap: 12 },
  field: { flex: 1, marginBottom: 16 },
  label: {
    marginBottom: 8,
    color: colors.muted,
    fontSize: 13,
    fontWeight: '700',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 14,
    backgroundColor: '#fafcf9',
  },
  input: {
    flex: 1,
    padding: 14,
    color: colors.ink,
    fontSize: 16,
    fontWeight: '700',
  },
  suffix: { paddingRight: 14, color: colors.muted, fontSize: 14 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 18 },
  chip: {
    paddingHorizontal: 13,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 20,
    backgroundColor: '#fff',
  },
  chipActive: { borderColor: colors.green, backgroundColor: colors.pale },
  chipText: { color: colors.muted, fontSize: 13, fontWeight: '600' },
  chipTextActive: { color: colors.green },
  button: {
    alignItems: 'center',
    marginTop: 18,
    padding: 17,
    borderRadius: 16,
    backgroundColor: colors.green,
  },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '800' },
  privacy: {
    marginTop: 13,
    color: colors.muted,
    fontSize: 12,
    textAlign: 'center',
  },
  productRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 13,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  productIcon: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 34,
    height: 34,
    borderRadius: 12,
    backgroundColor: colors.pale,
  },
  productText: { flex: 1, marginLeft: 12 },
  productName: { color: colors.ink, fontSize: 15, fontWeight: '700' },
  productAmount: { marginTop: 3, color: colors.muted, fontSize: 12 },
  remove: { color: '#9ca69e', fontSize: 24 },
  addProduct: {
    alignItems: 'center',
    marginTop: 16,
    padding: 13,
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: colors.green,
    borderRadius: 14,
  },
  addProductText: { color: colors.green, fontSize: 14, fontWeight: '700' },
  notice: {
    marginTop: 14,
    padding: 18,
    borderRadius: 18,
    backgroundColor: colors.pale,
  },
  noticeTitle: { color: colors.ink, fontSize: 14, fontWeight: '800' },
  noticeText: { marginTop: 5, color: colors.muted, fontSize: 13 },
  summary: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 18,
    padding: 18,
    borderRadius: 20,
    backgroundColor: colors.green,
  },
  summaryValue: { color: '#fff', fontSize: 18, fontWeight: '900' },
  summaryLabel: { marginTop: 3, color: '#d9e9df', fontSize: 11 },
  mealCard: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 18,
    backgroundColor: '#fff',
  },
  mealNumber: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 38,
    height: 38,
    borderRadius: 14,
    backgroundColor: colors.pale,
  },
  mealNumberAccent: { backgroundColor: '#f4e7c5' },
  mealNumberText: { color: colors.green, fontSize: 14, fontWeight: '900' },
  mealBody: { flex: 1, marginLeft: 13 },
  mealType: {
    color: colors.green,
    fontSize: 11,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
  mealName: {
    marginTop: 3,
    color: colors.ink,
    fontSize: 16,
    fontWeight: '800',
  },
  mealMeta: { marginTop: 5, color: colors.muted, fontSize: 12 },
  chevron: { color: colors.muted, fontSize: 28 },
  budgetCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 8,
    padding: 18,
    borderRadius: 18,
    backgroundColor: colors.pale,
  },
  budgetOk: { color: colors.green, fontSize: 25, fontWeight: '900' },
  prototypeNav: {
    position: 'absolute',
    right: 0,
    bottom: 18,
    left: 0,
    flexDirection: 'row',
    justifyContent: 'center',
  },
  navDot: { padding: 7 },
  dot: { width: 7, height: 7, borderRadius: 4, backgroundColor: '#bcc8be' },
  dotActive: { width: 22, backgroundColor: colors.green },
})
