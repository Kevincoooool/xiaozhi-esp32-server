<template>
  <div id="app">
    <div class="app-content" :class="{ 'auth-layout': !isLoggedIn }">
      <div v-if="!isLoggedIn">
        <Login v-if="!showRegistration" @show-registration="showRegistration = true" @login-success="handleLoginSuccess" />
        <Registration v-else @show-login="showRegistration = false" />
      </div>
      <div v-else class="main-layout">
        <role-setting v-if="currentView === 'RoleSetting'" 
          :device-id="selectedDeviceId"
        @back-to-panel="switchView('panel')"/>
        <panel v-else-if="currentView === 'panel'" 
          @go-home="switchView('main')" 
          @show-role="handleShowRole" 
          />
        <main-page v-else @enter-panel="switchView('panel')"/>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script>
import Login from './components/Login.vue';
import Registration from './components/Registration.vue';
import panel from './components/panel.vue';
import MainPage from './components/Main.vue';
import RoleSetting from './components/RoleSetting.vue';
import Footer from './components/Footer.vue';

export default {
  name: 'App',
  components: { 
    Login, 
    Registration, 
    panel, 
    MainPage, 
    RoleSetting,
    Footer 
  },
  data() {
    return {
      showRegistration: false,
      isLoggedIn: false,
      currentView: 'main',
      selectedDeviceId: null  // 添加selectedDeviceId状态
    };
  },
  methods: {
    handleLoginSuccess() {
      this.isLoggedIn = true;
      this.currentView = 'panel';
    },
    switchView(view) {
      console.log('Switching to view:', view); // 添加调试日志
      this.currentView = view;
    },
    handleShowRole(deviceId) {
      this.selectedDeviceId = deviceId;
      this.switchView('RoleSetting');
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
}

/* 登录注册页面的布局 */
.auth-layout {
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* 主要页面的布局 */
.main-layout {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>