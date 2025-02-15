<template>
  <div class="app-container">
    <NavBar current-tab="device" @tab-change="handleTabChange"/>

    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <router-link to="/control-panel">控制台</router-link> /
      <router-link to="/device-management">设备管理</router-link> /
      <span>配置角色</span>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <h1 class="page-title">配置角色: {{ deviceId }}</h1>

      <div class="form-section">
        <div class="form-group">
          <label>助手昵称</label>
          <input type="text" v-model="nickname" placeholder="小智" class="form-input" />
        </div>

        <div class="form-group">
          <label>角色模板</label>
          <div class="role-templates">
            <button 
              v-for="template in roleTemplates" 
              :key="template.id"
              :class="['template-btn', { active: selectedTemplate === template.id }]"
              @click="selectTemplate(template.id)"
            >
              {{ template.name }}
            </button>
          </div>
        </div>
        <div class="form-group">
          <label>角色介绍</label>
          <textarea 
            v-model="roleDescription" 
            class="form-textarea"
            :placeholder="'请输入角色介绍...'"
          ></textarea>
          <div class="char-count">{{ roleDescription.length }} / 2000</div>
        </div>

        <div class="form-group">
          <label>语言模型选择</label>
          <div class="model-select">
            <select v-model="selectedModules.LLM" class="form-input">
              <option v-for="model in moduleOptions.LLM" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
            <div class="model-description">
              除了"qwen-turbo"，其他模型通常会增加约 1 秒的延迟。改变模型后，建议清空记忆体，以免影响体验。
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>语音合成选择</label>
          <div class="model-select">
            <select v-model="selectedModules.TTS" class="form-input">
              <option v-for="model in moduleOptions.TTS" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>语音活动检测选择</label>
          <div class="model-select">
            <select v-model="selectedModules.VAD" class="form-input">
              <option v-for="model in moduleOptions.VAD" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>语音识别选择</label>
          <div class="model-select">
            <select v-model="selectedModules.ASR" class="form-input">
              <option v-for="model in moduleOptions.ASR" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button class="refresh-btn" @click="refreshModuleOptions">刷新配置选项</button>
          <button class="save-btn" @click="saveConfig">
            <i class="icon-save"></i>
            保存配置
          </button>
        </div>

        <div class="form-note">
          注意：保存配置后，需要重启设备，新的配置才会生效。。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import NavBar from './NavBar.vue';
import RoleTemplates from '../utils/RoleTemplates';
import { API_BASE_URL } from '../config/api';

const roleTemplates = RoleTemplates.getTemplates();

const nickname = ref('小智');
const selectedTemplate = ref('');
const selectedVoice = ref('qingchun');
const roleDescription = ref('');
const activeMemoryTab = ref('recent');
const memoryContent = ref('');
const selectedModel = ref('qianwen');

const baseUrl = API_BASE_URL;
const moduleOptions = ref({
  LLM: [],
  TTS: [],
  VAD: [],
  ASR: []
});

const selectedModules = ref({
  LLM: '',
  TTS: '',
  VAD: '',
  ASR: ''
});

const selectTemplate = (templateId) => {
  selectedTemplate.value = templateId;
  const template = RoleTemplates.getTemplateById(templateId);
  if (template) {
    roleDescription.value = template.description;
  }
};

const emit = defineEmits(['back-to-panel']);

const handleBack = () => {
  console.log('Triggering back-to-panel event'); // 添加调试日志
  emit('back-to-panel');
};

const handleTabChange = (tab) => {
  if (tab === 'device' || tab === 'home') {
    emit('back-to-panel');
  }
};

// 修改deviceId的定义，接收props
const props = defineProps({
  deviceId: {
    type: String,
    required: true
  }
});

// 使用props中的deviceId替换原来的静态值
const deviceId = ref(props.deviceId);

const loadModuleOptions = async () => {
  try {
    // First try to load from cache
    const cached = localStorage.getItem('moduleOptions');
    if (cached) {
      moduleOptions.value = JSON.parse(cached);
      return;
    }
    await refreshModuleOptions();
  } catch (error) {
    console.error('Error loading module options:', error);
  }
};

const refreshModuleOptions = async () => {
  try {
    const response = await fetch(`${baseUrl}/api/config/module-options`);
    const data = await response.json();
    if (data.success) {
      moduleOptions.value = data.data;
      // Update cache
      localStorage.setItem('moduleOptions', JSON.stringify(data.data));
    }
  } catch (error) {
    console.error('Error refreshing module options:', error);
  }
};

const saveConfig = async () => {
  try {
    const moduleOptionsData = localStorage.getItem('moduleOptions');
    if (!moduleOptionsData) {
      throw new Error('No module options data available');
    }

    // Replace {{assistant_name}} with current nickname in role description
    const processedDescription = roleDescription.value.replace(/{{assistant_name}}/g, nickname.value);

    // Prepare the configuration including full module settings
    const config = {
      id: props.deviceId,
      config: {
        selected_module: selectedModules.value,
        prompt: processedDescription,
        nickname: nickname.value, // Add nickname to config
        modules: {
          LLM: {},
          TTS: {},
          ASR: {},
          VAD: {}
        }
      }
    };
    
    const response = await fetch(`${baseUrl}/api/config/save_device_config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    });
    
    const data = await response.json();
    if (data.success) {
      // Save the original description and nickname to local storage
      localStorage.setItem(`deviceConfig_${props.deviceId}`, JSON.stringify({
        selected_module: selectedModules.value,
        prompt: roleDescription.value,
        nickname: nickname.value
      }));
      alert('保存成功');
    } else {
      throw new Error(data.message || '保存失败');
    }
  } catch (error) {
    console.error('Error saving config:', error);
    alert(error.message || '保存失败');
  }
};

const loadDeviceConfig = async () => {
  try {
    // First try to get config from local storage
    const localConfig = localStorage.getItem(`deviceConfig_${props.deviceId}`);
    if (localConfig) {
      const config = JSON.parse(localConfig);
      selectedModules.value = config.selected_module || {};
      roleDescription.value = config.prompt || '';
      nickname.value = config.nickname || '小智'; // Load saved nickname
      return;
    }

    // If no local config, fetch from server
    const response = await fetch(`${baseUrl}/api/config/devices`);
    const data = await response.json();
    if (data.success) {
      const deviceConfig = data.data.find(d => d.id === props.deviceId);
      if (deviceConfig) {
        selectedModules.value = deviceConfig.config.selected_module || {};
        roleDescription.value = deviceConfig.config.prompt || '';
        nickname.value = deviceConfig.config.nickname || '小智'; // Load nickname from server
        
        // Save to local storage
        localStorage.setItem(`deviceConfig_${props.deviceId}`, JSON.stringify({
          selected_module: deviceConfig.config.selected_module,
          prompt: deviceConfig.config.prompt,
          nickname: deviceConfig.config.nickname
        }));
      }
    }
  } catch (error) {
    console.error('Error loading device config:', error);
  }
};

onMounted(async () => {
  await Promise.all([
    loadModuleOptions(),
    loadDeviceConfig()
  ]);
});

const resetConfig = async () => {
  await loadDeviceConfig();
};
</script>

<style scoped>
.app-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.breadcrumb {
  padding: 12px 24px;
  background-color: #f0f2f5;
}

.main-content {
  flex: 1;
  max-width: 1000px;
  margin: 0 auto;
  padding: 16px 24px;
  overflow: auto;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
}

.form-section {
  background: white;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-input,
.form-textarea,
.voice-select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.form-textarea {
  min-height: 100px;
  max-height: 200px;
  resize: vertical;
}

.role-templates {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.template-btn {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 13px;
}

.voice-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.voice-player {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
}

.memory-tabs {
  display: flex;
  margin-bottom: 8px;
}

.tab-btn {
  padding: 6px 12px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  color: #666;
  font-size: 13px;
}

.model-select {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.model-description {
  color: #666;
  font-size: 12px;
  line-height: 1.4;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.save-btn,
.cancel-btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 14px;
}

.form-note {
  margin-top: 12px;
  color: #666;
  font-size: 12px;
}

.char-count {
  text-align: right;
  color: #999;
  font-size: 12px;
  margin-top: 2px;
}

/* 优化滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.refresh-btn {
  padding: 8px 16px;
  margin-right: 12px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:hover {
  background: #f5f5f5;
}

.save-btn {
  padding: 8px 24px;
  border-radius: 4px;
  font-size: 14px;
  background: #4178EE;
  color: white;
  border: none;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.save-btn:hover {
  background: #2856c8;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(65, 120, 238, 0.2);
}

.save-btn:active {
  transform: translateY(0);
  box-shadow: none;
}

.icon-save {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M17 3H5C3.89 3 3 3.9 3 5V19C3 20.1 3.89 21 5 21H19C20.1 21 21 20.1 21 19V7L17 3ZM12 19C10.34 19 9 17.66 9 16C9 14.34 10.34 13 12 13C13.66 13 15 14.34 15 16C15 17.66 13.66 19 12 19ZM15 9H5V5H15V9Z'/%3E%3C/svg%3E");
  background-size: contain;
}
</style>