<template>
    <div class="login-container">
      <h1>登录</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input type="text" v-model="username" id="username" required />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" v-model="password" id="password" required />
        </div>
        <button type="submit" :disabled="isLoading">登录</button>
      </form>
      <p>还没注册账户? <a href="#" @click.prevent="$emit('show-registration')">点击注册</a></p>
    </div>
  </template>
  
  <script>
  import { API_BASE_URL } from '../config/api';

  export default {
    data() {
      return {
        username: '',
        password: '',
        isLoading: false
      };
    },
    methods: {
      async handleLogin() {
        if (!this.username || !this.password) {
          alert('请输入用户名和密码！');
          return;
        }
  
        this.isLoading = true;
        try {
          const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: this.username,
              password: this.password
            })
          });
  
          const data = await response.json();
          
          if (data.success) {
            // 登录成功
            this.$emit('login-success');
          } else {
            // 登录失败
            alert(data.message || '登录失败');
          }
        } catch (error) {
          console.error('Login error:', error);
          alert('登录失败，请检查网络连接');
        } finally {
          this.isLoading = false;
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .login-container {
    max-width: 420px;
    margin: 20px auto;
    padding: 40px 50px;
    border: none;
    border-radius: 12px;
    background-color: #ffffff;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    transition: all 0.3s ease;
  }
  
  h1 {
    text-align: center;
    color: #2c3e50;
    font-size: 28px;
    margin-bottom: 25px;
    font-weight: 600;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #4a5568;
  }
  
  input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: #f8fafc;
    transition: all 0.3s ease;
    font-size: 15px;
  }
  
  input:focus {
    outline: none;
    border-color: #28a745;
    box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.2);
  }
  
  button {
    width: 100%;
    padding: 12px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.3s ease;
    margin-top: 10px;
  }
  
  button:hover {
    background-color: #218838;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
  }

  button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  p {
    margin-top: 20px;
    color: #666;
    font-size: 14px;
  }
  
  a {
    color: #28a745;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
  }
  
  a:hover {
    color: #218838;
    text-decoration: underline;
  }
  </style>