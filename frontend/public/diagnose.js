/**
 * 前端图表问题自动诊断脚本
 * 在浏览器控制台中粘贴并运行此脚本
 */
(function diagnoseChartIssue() {
  console.log('%c========================================', 'color: #0066ff');
  console.log('%c前端图表问题诊断脚本', 'color: #0066ff; font-size: 16px; font-weight: bold');
  console.log('%c========================================', 'color: #0066ff');
  console.log('');

  // 诊断结果收集
  const results = {
    timestamp: new Date().toISOString(),
    issues: [],
    warnings: [],
    info: []
  };

  // 1. 检查 Chart.js 是否加载
  console.log('%c1. 检查 Chart.js 加载状态', 'color: #009900; font-weight: bold');
  try {
    if (typeof Chart !== 'undefined') {
      console.log(`✓ Chart.js 已加载，版本: ${Chart.version || '未知'}`);
      results.info.push({ check: 'Chart.js', status: 'loaded', version: Chart.version });
    } else {
      console.error('✗ Chart.js 未加载！');
      results.issues.push({ check: 'Chart.js', error: 'Chart.js not defined' });
    }
  } catch (e) {
    console.error('✗ Chart.js 检查失败:', e.message);
    results.issues.push({ check: 'Chart.js', error: e.message });
  }
  console.log('');

  // 2. 检查 Canvas 元素
  console.log('%c2. 检查 Canvas 元素', 'color: #009900; font-weight: bold');
  const canvases = document.querySelectorAll('canvas');
  console.log(`找到 ${canvases.length} 个 canvas 元素`);

  canvases.forEach((canvas, index) => {
    console.log(`\nCanvas #${index + 1}:`);
    console.log(`  - Width: ${canvas.width}px`);
    console.log(`  - Height: ${canvas.height}px`);
    console.log(`  - CSS Width: ${getComputedStyle(canvas).width}`);
    console.log(`  - CSS Height: ${getComputedStyle(canvas).height}`);
    console.log(`  - Display: ${getComputedStyle(canvas).display}`);
    console.log(`  - Position: ${getComputedStyle(canvas).position}`);

    // 检查 Canvas 尺寸问题
    if (canvas.width === 0 || canvas.height === 0) {
      console.error('  ⚠ Canvas 尺寸为 0，可能无法显示图表！');
      results.warnings.push({ check: 'Canvas', index: index, issue: 'Zero size' });
    }
  });

  if (canvases.length === 0) {
    console.error('✗ 未找到任何 canvas 元素！');
    results.issues.push({ check: 'Canvas', error: 'No canvas elements found' });
  }
  console.log('');

  // 3. 检查 Vue 应用
  console.log('%c3. 检查 Vue 应用', 'color: #009900; font-weight: bold');
  try {
    const app = document.querySelector('#app');
    if (app) {
      console.log('✓ Vue 应用容器 (#app) 存在');
      results.info.push({ check: 'Vue App', status: 'found' });
    } else {
      console.error('✗ Vue 应用容器 (#app) 不存在！');
      results.issues.push({ check: 'Vue App', error: 'Container not found' });
    }
  } catch (e) {
    console.error('✗ Vue 应用检查失败:', e.message);
    results.issues.push({ check: 'Vue App', error: e.message });
  }
  console.log('');

  // 4. 检查 API 基础配置
  console.log('%c4. 检查 API 配置', 'color: #009900; font-weight: bold');
  const apiBaseUrl = window.location.origin + '/api';
  console.log(`API 基础 URL: ${apiBaseUrl}`);

  // 测试 API 连接
  fetch(apiBaseUrl + '/dashboard/charts', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })
    .then(response => {
      console.log(`✓ API 连接成功，状态码: ${response.status}`);
      results.info.push({ check: 'API', status: 'connected', statusCode: response.status });
      return response.json();
    })
    .then(data => {
      console.log('✓ API 响应数据:', data);
      results.info.push({ check: 'API Response', data: data });
    })
    .catch(error => {
      console.error('✗ API 连接失败:', error.message);
      results.issues.push({ check: 'API', error: error.message });
    });
  console.log('');

  // 5. 检查图表卡片元素
  console.log('%c5. 检查图表卡片', 'color: #009900; font-weight: bold');
  const chartCards = document.querySelectorAll('.chart-card');
  console.log(`找到 ${chartCards.length} 个图表卡片`);

  chartCards.forEach((card, index) => {
    console.log(`\nChart Card #${index + 1}:`);
    console.log(`  - HTML: ${card.outerHTML.substring(0, 100)}...`);
    console.log(`  - Display: ${getComputedStyle(card).display}`);

    // 检查权限提示
    const permissionDenied = card.querySelector('.permission-denied');
    if (permissionDenied) {
      console.warn('  ⚠ 该图表显示"权限被拒绝"');
      results.warnings.push({ check: 'Chart Card', index: index, issue: 'Permission denied' });
    }
  });
  console.log('');

  // 6. 检查全局错误监听
  console.log('%c6. 检查最近的全局错误', 'color: #009900; font-weight: bold');
  const originalError = console.error;
  let errorCount = 0;
  console.error = function(...args) {
    errorCount++;
    console.error = originalError;
  };

  // 7. 检查网络请求（简化版）
  console.log('%c7. 网络请求检查', 'color: #009900; font-weight: bold');
  console.log('正在检查最近的网络请求...');
  console.log('提示：请查看 Network 标签页获取详细信息');
  console.log('');

  // 8. 生成诊断报告
  console.log('%c========================================', 'color: #0066ff');
  console.log('%c诊断报告', 'color: #0066ff; font-size: 16px; font-weight: bold');
  console.log('%c========================================', 'color: #0066ff');
  console.log('');

  console.log('%c问题统计:', 'color: #ff6600; font-weight: bold');
  console.log(`  - 问题: ${results.issues.length} 个`);
  console.log(`  - 警告: ${results.warnings.length} 个`);
  console.log(`  - 信息: ${results.info.length} 个`);

  if (results.issues.length > 0) {
    console.log('\n%c发现的问题:', 'color: #ff0000; font-weight: bold');
    results.issues.forEach((issue, i) => {
      console.log(`  ${i + 1}. ${issue.check}: ${issue.error || issue.issue}`);
    });
  }

  if (results.warnings.length > 0) {
    console.log('\n%c警告:', 'color: #ff9900; font-weight: bold');
    results.warnings.forEach((warning, i) => {
      console.log(`  ${i + 1}. ${warning.check}: ${warning.issue}`);
    });
  }

  console.log('\n%c诊断数据（复制此信息）:', 'color: #009900; font-weight: bold');
  console.log(JSON.stringify(results, null, 2));

  console.log('');
  console.log('%c========================================', 'color: #0066ff');
  console.log('%c诊断完成', 'color: #0066ff');
  console.log('%c========================================', 'color: #0066ff');

  return results;
})();
