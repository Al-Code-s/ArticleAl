import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import App from './App';
import './index.css';

// 设置dayjs中文
dayjs.locale('zh-cn');

// 创建React Query客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5分钟
    },
  },
});

// Ant Design主题配置 - 现代深色调
const theme = {
  token: {
    colorPrimary: '#38BDF8',
    colorSuccess: '#4FD1C5',
    colorWarning: '#F59E0B',
    colorError: '#F87171',
    colorInfo: '#38BDF8',
    colorBgBase: '#FFFFFF',
    colorTextBase: '#0F172A',
    borderRadius: 8,
    fontSize: 14,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  components: {
    Layout: {
      headerBg: '#FFFFFF',
      siderBg: '#FFFFFF',
      bodyBg: '#F8FAFC',
    },
    Menu: {
      itemBg: '#FFFFFF',
      itemSelectedBg: '#F1F5F9',
      itemSelectedColor: '#38BDF8',
      itemHoverBg: '#F8FAFC',
      itemHoverColor: '#38BDF8',
    },
    Card: {
      borderRadiusLG: 12,
      paddingLG: 24,
    },
    Button: {
      borderRadius: 8,
      controlHeight: 40,
      fontWeight: 500,
    },
    Input: {
      borderRadius: 8,
      controlHeight: 40,
    },
    Table: {
      headerBg: '#F8FAFC',
      headerColor: '#64748B',
      borderColor: '#E2E8F0',
    },
  },
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider locale={zhCN} theme={theme}>
          <App />
        </ConfigProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
