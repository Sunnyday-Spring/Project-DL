// src/services/api.js

import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// ===== Face Recognition API =====

export const detectFace = async (imageFile) => {
  const formData = new FormData()
  formData.append('file', imageFile)
  
  const response = await api.post('/detect', formData)
  return response.data
}

export const registerFace = async (userId, imageFile) => {
  const formData = new FormData()
  formData.append('user_id', userId)
  formData.append('file', imageFile)
  
  const response = await api.post('/register', formData)
  return response.data
}

export const verifyFace = async (userId, imageFile) => {
  const formData = new FormData()
  formData.append('user_id', userId)
  formData.append('file', imageFile)
  
  const response = await api.post('/verify', formData)
  return response.data
}

// ===== Identify Face (Real-time Login) =====
export const identifyFace = async (imageFile) => {
  const formData = new FormData()
  formData.append('file', imageFile)
  
  const response = await api.post('/identify', formData)
  return response.data
}

// ===== NEW: Detect Blink (Liveness Check) =====
/**
 * ส่งภาพไปตรวจสอบการกระพริบตา (Liveness Detection)
 */
export const detectBlink = async (imageFile) => {
  const formData = new FormData()
  formData.append('file', imageFile)
  
  const response = await api.post('/detect-blink', formData)
  return response.data
}

export const getUsers = async () => {
  const response = await api.get('/users')
  return response.data
}

export const deleteUser = async (userId) => {
  const response = await api.delete(`/user/${userId}`)
  return response.data
}

export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api