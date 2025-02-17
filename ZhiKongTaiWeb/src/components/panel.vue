<template>
  <div class="app">
    <NavBar current-tab="device" @tab-change="handleTabChange"/>
    <main class="content">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link> /
        <span>设备管理</span>
      </div>
      
      <template v-if="devices.length > 0">
        <div class="device-list">
          <DeviceCard
            v-for="device in devices"
            :key="device.id"
            :device-id="device.id"
            :device-note="device.note"
            :device-type="device.type"
            :last-activity="formatLastActivity(device.config.last_chat_time)"
            :selected-modules="device.config.selected_module"
            :device-config="device.config"
            @configure="handleRoleConfig(device)"
            @voiceprint="handleVoiceprint(device)"
            @history="handleHistory(device)"
            @delete="handleDelete(device)"
          />
        </div>
      </template>
      <template v-else>
        <div class="empty-state">
          <div class="empty-message">
            <i class="icon-info"></i>
            <p>目前没有设备，请确认是否启用私有配置，并且和设备进行一次对话</p>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import NavBar from './NavBar.vue';
import DeviceCard from './DeviceCard.vue';
import { API_BASE_URL } from '../config/api';

const router = useRouter();
const baseUrl = API_BASE_URL;
const devices = ref([]);

const formatLastActivity = (timestamp) => {
  if (!timestamp) return '从未对话';
  
  const now = Date.now();
  const lastChat = timestamp * 1000;
  const diffMinutes = Math.floor((now - lastChat) / (1000 * 60));
  
  if (diffMinutes < 60) {
    return `${diffMinutes} 分钟前`;
  }
  
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours} 小时前`;
  }
  
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} 天前`;
};

const handleRoleConfig = (device) => {
  router.push(`/role-setting/${device.id}`);
};

const handleVoiceprint = (device) => {
  console.log('Voiceprint device:', device.id);
};

const handleHistory = (device) => {
  console.log('History device:', device.id);
};

const handleDelete = async (device) => {
  try {
    const response = await fetch(`${baseUrl}/api/config/delete_device`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ device_id: device.id })
    });
    
    const data = await response.json();
    if (data.success) {
      devices.value = devices.value.filter(d => d.id !== device.id);
      alert('设备已删除');
    } else {
      throw new Error(data.message || '删除失败');
    }
  } catch (error) {
    console.error('Error deleting device:', error);
    alert('删除设备失败: ' + error.message);
  }
};

const handleTabChange = (tab) => {
  if (tab === 'home') {
    router.push('/');
  }
};

// Load devices on mount
onMounted(async () => {
  try {
    const response = await fetch(`${baseUrl}/api/config/devices`);
    const data = await response.json();
    if (data.success) {
      devices.value = data.data.map(device => ({
        ...device,
        type: '面包板（WiFi）',
        version: '0.9.9',
        lastActivity: '3 天前',
        note: ''
      }));
    }
  } catch (error) {
    console.error('Error loading devices:', error);
  }
});
</script>

<style scoped>
.app {
  min-height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background-color: #001529;
  color: white;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  margin-right: 40px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.8;
}

.nav {
  display: flex;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  color: white;
  text-decoration: none;
}

.nav-item.active {
  background-color: #4178EE;
}

.icon-device {
  margin-right: 8px;
}

.content {
  flex: 1;
  padding: 20px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 20px;
  color: #666;
}

.breadcrumb a {
  color: #666;
  text-decoration: none;
}

.action-bar {
  margin-bottom: 20px;
}

.add-device-btn {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.icon-plus {
  margin-right: 8px;
}

.device-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.device-card {
  background: white;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.device-id {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
}

.note {
  color: #4178EE;
  font-size: 14px;
  font-weight: normal;
}

.device-details p {
  margin-bottom: 12px;
}

.ota-upgrade {
  display: inline-flex;
  align-items: center;
  margin-left: 16px;
}

.device-actions {
  display: flex;
  margin-top: 20px;
}

.action-btn {
  padding: 8px 16px;
  margin-right: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.action-btn.primary {
  background: #4178EE;
  color: white;
  border-color: #4178EE;
}

.action-btn.danger {
  color: #f56c6c;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.empty-message {
  text-align: center;
  color: #666;
  padding: 24px;
}

.empty-message p {
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.6;
}

.icon-info {
  display: inline-block;
  width: 24px;
  height: 24px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23999'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z'/%3E%3C/svg%3E");
  background-size: contain;
  opacity: 0.6;
}
</style>