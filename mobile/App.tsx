import { StatusBar } from 'expo-status-bar'
import { useEffect, useState } from 'react'
import {
  ActivityIndicator,
  SafeAreaView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native'

const apiUrl = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000'

type ApiState = 'loading' | 'online' | 'offline'

export default function App() {
  const [apiState, setApiState] = useState<ApiState>('loading')

  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then((response) => {
        if (!response.ok) throw new Error('API is unavailable')
        setApiState('online')
      })
      .catch(() => setApiState('offline'))
  }, [])

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View style={styles.container}>
        <Text style={styles.eyebrow}>AI-ПЛАНИРОВЩИК ПИТАНИЯ</Text>
        <Text style={styles.title}>Рацион под ваши цели и бюджет</Text>
        <Text style={styles.description}>
          Приложение учтёт параметры пользователя, ограничения по продуктам и
          целевые значения КБЖУ.
        </Text>
        <TouchableOpacity
          accessibilityRole="button"
          disabled
          style={styles.button}
        >
          <Text style={styles.buttonText}>Создать план — скоро</Text>
        </TouchableOpacity>
        <View style={styles.statusRow}>
          {apiState === 'loading' && (
            <ActivityIndicator color="#26733d" size="small" />
          )}
          <Text style={styles.statusText}>
            {apiState === 'loading' && 'Проверяем API…'}
            {apiState === 'online' && 'API подключён'}
            {apiState === 'offline' && 'API недоступен'}
          </Text>
        </View>
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f3f7f3',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 28,
  },
  eyebrow: {
    color: '#26733d',
    fontSize: 13,
    fontWeight: '800',
    letterSpacing: 1.2,
  },
  title: {
    marginTop: 14,
    color: '#17211b',
    fontSize: 43,
    fontWeight: '800',
    lineHeight: 47,
  },
  description: {
    marginTop: 20,
    color: '#526158',
    fontSize: 17,
    lineHeight: 27,
  },
  button: {
    alignItems: 'center',
    marginTop: 32,
    padding: 16,
    borderRadius: 14,
    backgroundColor: '#26733d',
    opacity: 0.75,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    minHeight: 24,
    marginTop: 20,
  },
  statusText: {
    marginLeft: 8,
    color: '#26733d',
    fontSize: 14,
    fontWeight: '700',
  },
})
