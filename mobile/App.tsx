import { StatusBar } from 'expo-status-bar'
import { useState } from 'react'
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native'

type Screen = 'profile' | 'pantry' | 'loading' | 'plan' | 'error'
type NavigationScreen = 'profile' | 'pantry' | 'plan'
type Goal = 'снижение веса' | 'поддержание веса' | 'набор веса'
type PantryKey = 'buckwheat' | 'eggs' | 'beans'

type ApiMeal = {
  name: string
  meal_type: string
  ingredients: { name: string; amount_g: number }[]
  cook_time_min: number
}

type PlanResponse = {
  request_id: string
  days: { day: number; meals: ApiMeal[] }[]
  shopping_list: { name: string; amount_g: number; estimated_cost: number }[]
  totals: {
    cost: number
    currency: string
    calories: number
    protein_g: number
    fat_g: number
    carbs_g: number
    target_calories_per_day: number
  }
  validation: {
    schema_valid: boolean
    constraints_valid: boolean
    retry_count: number
  }
}

const screens: NavigationScreen[] = ['profile', 'pantry', 'plan']
const apiUrl = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000'

function initialScreen(): NavigationScreen {
  if (typeof window === 'undefined') return 'profile'
  const requested = new URLSearchParams(window.location.search).get('screen')
  return screens.includes(requested as NavigationScreen)
    ? (requested as NavigationScreen)
    : 'profile'
}

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
  onChangeText,
}: {
  label: string
  value: string
  suffix?: string
  onChangeText: (value: string) => void
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.inputRow}>
        <TextInput
          keyboardType="numeric"
          onChangeText={onChangeText}
          style={styles.input}
          value={value}
        />
        {suffix && <Text style={styles.suffix}>{suffix}</Text>}
      </View>
    </View>
  )
}

function Chip({
  children,
  active = false,
  onPress,
}: {
  children: string
  active?: boolean
  onPress: () => void
}) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={[styles.chip, active && styles.chipActive]}
    >
      <Text style={[styles.chipText, active && styles.chipTextActive]}>
        {children}
      </Text>
    </Pressable>
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

function ProfileScreen({
  height,
  weight,
  budget,
  goal,
  maxCookTime,
  error,
  setHeight,
  setWeight,
  setBudget,
  setGoal,
  setMaxCookTime,
  next,
}: {
  height: string
  weight: string
  budget: string
  goal: Goal
  maxCookTime: number
  error: string
  setHeight: (value: string) => void
  setWeight: (value: string) => void
  setBudget: (value: string) => void
  setGoal: (value: Goal) => void
  setMaxCookTime: (value: number) => void
  next: () => void
}) {
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
          <Field
            label="Рост"
            value={height}
            suffix="см"
            onChangeText={setHeight}
          />
          <Field
            label="Вес"
            value={weight}
            suffix="кг"
            onChangeText={setWeight}
          />
        </View>
        <Field
          label="Бюджет на неделю"
          value={budget}
          suffix="₽"
          onChangeText={setBudget}
        />
        <Text style={styles.label}>Цель</Text>
        <View style={styles.chips}>
          <Chip
            active={goal === 'снижение веса'}
            onPress={() => setGoal('снижение веса')}
          >
            Снизить вес
          </Chip>
          <Chip
            active={goal === 'поддержание веса'}
            onPress={() => setGoal('поддержание веса')}
          >
            Поддерживать
          </Chip>
          <Chip
            active={goal === 'набор веса'}
            onPress={() => setGoal('набор веса')}
          >
            Набрать вес
          </Chip>
        </View>
        <Text style={styles.label}>Сколько готовить одно блюдо</Text>
        <View style={styles.chips}>
          <Chip active={maxCookTime === 15} onPress={() => setMaxCookTime(15)}>
            до 15 мин
          </Chip>
          <Chip active={maxCookTime === 30} onPress={() => setMaxCookTime(30)}>
            до 30 мин
          </Chip>
          <Chip
            active={maxCookTime === 240}
            onPress={() => setMaxCookTime(240)}
          >
            не важно
          </Chip>
        </View>
        {error ? <Text style={styles.validationError}>{error}</Text> : null}
      </View>
      <PrimaryButton title="Продолжить" onPress={next} />
      <Text style={styles.privacy}>
        Ваши данные используются только для составления плана
      </Text>
    </ScrollView>
  )
}

const pantryOptions: Record<
  PantryKey,
  { name: string; amount: string; amount_g: number }
> = {
  buckwheat: { name: 'Гречка', amount: '450 г', amount_g: 450 },
  eggs: { name: 'Яйца', amount: '6 шт', amount_g: 360 },
  beans: {
    name: 'Фасоль консервированная',
    amount: '1 банка',
    amount_g: 400,
  },
}

function PantryScreen({
  selected,
  excluded,
  togglePantry,
  toggleExcluded,
  next,
}: {
  selected: PantryKey[]
  excluded: string[]
  togglePantry: (value: PantryKey) => void
  toggleExcluded: (value: string) => void
  next: () => void
}) {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Header
        step="Шаг 2 из 2"
        title="Что уже есть дома?"
        subtitle="Учтём запасы, чтобы покупать меньше и не выбрасывать продукты."
      />
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Ваши продукты</Text>
        {(
          Object.entries(pantryOptions) as [
            PantryKey,
            (typeof pantryOptions)[PantryKey],
          ][]
        ).map(([key, item]) => (
          <Pressable
            key={key}
            onPress={() => togglePantry(key)}
            style={styles.productRow}
          >
            <View style={styles.productIcon}>
              <Text>{selected.includes(key) ? '✓' : '＋'}</Text>
            </View>
            <View style={styles.productText}>
              <Text style={styles.productName}>{item.name}</Text>
              <Text style={styles.productAmount}>{item.amount}</Text>
            </View>
            <Text style={styles.remove}>
              {selected.includes(key) ? '×' : ''}
            </Text>
          </Pressable>
        ))}
        <View style={styles.addProduct}>
          <Text style={styles.addProductText}>
            Нажмите продукт, чтобы добавить или убрать
          </Text>
        </View>
      </View>
      <View style={styles.notice}>
        <Text style={styles.noticeTitle}>Ограничения</Text>
        <View style={[styles.chips, styles.restrictionChips]}>
          <Chip
            active={excluded.includes('арахис')}
            onPress={() => toggleExcluded('арахис')}
          >
            Без арахиса
          </Chip>
          <Chip
            active={excluded.includes('сельдерей')}
            onPress={() => toggleExcluded('сельдерей')}
          >
            Без сельдерея
          </Chip>
        </View>
      </View>
      <PrimaryButton title="Составить план" onPress={next} />
      <Text style={styles.privacy}>
        Обычно генерация занимает меньше минуты
      </Text>
    </ScrollView>
  )
}

function PlanScreen({ plan, budget }: { plan: PlanResponse; budget: number }) {
  const meals = plan.days[0]?.meals ?? []
  const mealTypes: Record<string, string> = {
    breakfast: 'Завтрак',
    lunch: 'Обед',
    dinner: 'Ужин',
    snack: 'Перекус',
  }
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Header
        step="План готов"
        title="Понедельник"
        subtitle="Рацион укладывается в бюджет и использует продукты из ваших запасов."
      />
      <View style={styles.summary}>
        <View>
          <Text style={styles.summaryValue}>
            {Math.round(plan.totals.target_calories_per_day)}
          </Text>
          <Text style={styles.summaryLabel}>цель ккал/день</Text>
        </View>
        <View>
          <Text style={styles.summaryValue}>
            {Math.round(plan.totals.protein_g / Math.max(1, plan.days.length))}{' '}
            г
          </Text>
          <Text style={styles.summaryLabel}>белок</Text>
        </View>
        <View>
          <Text style={styles.summaryValue}>
            {Math.round(plan.totals.cost)} ₽
          </Text>
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
            <Text style={styles.mealType}>
              {mealTypes[meal.meal_type] ?? meal.meal_type}
            </Text>
            <Text style={styles.mealName}>{meal.name}</Text>
            <Text style={styles.mealMeta}>
              {meal.ingredients.length} ингредиента · {meal.cook_time_min} мин
            </Text>
          </View>
          <Text style={styles.chevron}>›</Text>
        </View>
      ))}
      <View style={styles.budgetCard}>
        <View>
          <Text style={styles.noticeTitle}>Бюджет недели</Text>
          <Text style={styles.noticeText}>
            Осталось {Math.max(0, Math.round(budget - plan.totals.cost))} ₽ из{' '}
            {Math.round(budget)} ₽
          </Text>
        </View>
        <Text style={styles.budgetOk}>✓</Text>
      </View>
      <PrimaryButton title="Открыть список покупок" onPress={() => undefined} />
    </ScrollView>
  )
}

function LoadingScreen() {
  return (
    <View style={styles.stateScreen}>
      <ActivityIndicator color={colors.green} size="large" />
      <Text style={styles.stateTitle}>Составляем рацион…</Text>
      <Text style={styles.stateText}>
        Проверяем ограничения, бюджет и продукты дома
      </Text>
    </View>
  )
}

function ErrorScreen({
  message,
  retry,
}: {
  message: string
  retry: () => void
}) {
  return (
    <View style={styles.stateScreen}>
      <Text style={styles.errorIcon}>!</Text>
      <Text style={styles.stateTitle}>Не удалось создать план</Text>
      <Text style={styles.stateText}>{message}</Text>
      <PrimaryButton title="Попробовать ещё раз" onPress={retry} />
    </View>
  )
}

export default function App() {
  const [screen, setScreen] = useState<Screen>(initialScreen)
  const [plan, setPlan] = useState<PlanResponse | null>(null)
  const [error, setError] = useState('Проверьте соединение и повторите запрос')
  const [profileError, setProfileError] = useState('')
  const [height, setHeight] = useState('178')
  const [weight, setWeight] = useState('74')
  const [budget, setBudget] = useState('3500')
  const [goal, setGoal] = useState<Goal>('поддержание веса')
  const [maxCookTime, setMaxCookTime] = useState(30)
  const [pantry, setPantry] = useState<PantryKey[]>(['buckwheat', 'beans'])
  const [excluded, setExcluded] = useState<string[]>(['арахис', 'сельдерей'])

  function continueToPantry() {
    const parsedHeight = Number(height)
    const parsedWeight = Number(weight)
    const parsedBudget = Number(budget)
    if (
      !Number.isFinite(parsedHeight) ||
      parsedHeight < 120 ||
      parsedHeight > 230
    ) {
      setProfileError('Рост должен быть от 120 до 230 см')
      return
    }
    if (
      !Number.isFinite(parsedWeight) ||
      parsedWeight < 35 ||
      parsedWeight > 250
    ) {
      setProfileError('Вес должен быть от 35 до 250 кг')
      return
    }
    if (!Number.isFinite(parsedBudget) || parsedBudget <= 0) {
      setProfileError('Укажите бюджет больше нуля')
      return
    }
    setProfileError('')
    setScreen('pantry')
  }

  function togglePantry(value: PantryKey) {
    setPantry((current) =>
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value],
    )
  }

  function toggleExcluded(value: string) {
    setExcluded((current) =>
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value],
    )
  }

  async function generatePlan() {
    setScreen('loading')
    try {
      const response = await fetch(`${apiUrl}/api/v1/ai/meal-plans`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: { height_cm: Number(height), weight_kg: Number(weight) },
          goal,
          budget: { amount: Number(budget), currency: 'RUB' },
          days: 7,
          restrictions: excluded.map((item) => `без ${item}`),
          excluded_products: excluded,
          pantry: pantry.map((key) => ({
            name: pantryOptions[key].name,
            amount_g: pantryOptions[key].amount_g,
          })),
          max_cook_time_min: maxCookTime,
        }),
      })
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(
          body.message ?? body.detail ?? `Ошибка API: ${response.status}`,
        )
      }
      setPlan((await response.json()) as PlanResponse)
      setScreen('plan')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Неизвестная ошибка')
      setScreen('error')
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View style={styles.phone}>
        {screen === 'profile' && (
          <ProfileScreen
            height={height}
            weight={weight}
            budget={budget}
            goal={goal}
            maxCookTime={maxCookTime}
            error={profileError}
            setHeight={setHeight}
            setWeight={setWeight}
            setBudget={setBudget}
            setGoal={setGoal}
            setMaxCookTime={setMaxCookTime}
            next={continueToPantry}
          />
        )}
        {screen === 'pantry' && (
          <PantryScreen
            selected={pantry}
            excluded={excluded}
            togglePantry={togglePantry}
            toggleExcluded={toggleExcluded}
            next={generatePlan}
          />
        )}
        {screen === 'loading' && <LoadingScreen />}
        {screen === 'plan' && plan && (
          <PlanScreen plan={plan} budget={Number(budget)} />
        )}
        {screen === 'error' && (
          <ErrorScreen message={error} retry={generatePlan} />
        )}
        {screen !== 'loading' && screen !== 'error' && (
          <View style={styles.prototypeNav}>
            {screens.map((item) => (
              <Pressable
                key={item}
                onPress={() =>
                  item !== 'plan' || plan ? setScreen(item) : undefined
                }
                style={styles.navDot}
              >
                <View
                  style={[styles.dot, screen === item && styles.dotActive]}
                />
              </Pressable>
            ))}
          </View>
        )}
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
  validationError: {
    marginTop: 4,
    color: '#a63d32',
    fontSize: 13,
    fontWeight: '700',
  },
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
  restrictionChips: { marginTop: 12, marginBottom: 0 },
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
  stateScreen: { flex: 1, justifyContent: 'center', padding: 32 },
  stateTitle: {
    marginTop: 22,
    color: colors.ink,
    fontSize: 26,
    fontWeight: '800',
    textAlign: 'center',
  },
  stateText: {
    marginTop: 10,
    color: colors.muted,
    fontSize: 15,
    lineHeight: 23,
    textAlign: 'center',
  },
  errorIcon: {
    alignSelf: 'center',
    width: 52,
    height: 52,
    paddingTop: 7,
    borderRadius: 26,
    backgroundColor: '#f7dfdc',
    color: '#a63d32',
    fontSize: 28,
    fontWeight: '900',
    textAlign: 'center',
  },
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
