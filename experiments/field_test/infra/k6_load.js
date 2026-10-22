// 生产现场实验流量生成器：持续压被测服务正常路径
// /search（连接池+LRU 缓存路径）+ /downstream（经 toxiproxy 代理）
// vus=3、高迭代次数（等效常驻）；F1/F2/F3 注入后由该流量放大信号
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 3,
  // stages 1000h ≈ 等效常驻（避免 k6 默认 10 分钟时长限制导致流量缺口）
  stages: [{ duration: '1000h', target: 3 }],
  discardResponseBodies: false,
};

export default function () {
  // 随机 query：避免固定 key 命中 LRU 缓存而短路连接池路径（泄漏/缓存信号需要真实未命中流量）
  const q = 'k6-' + __ITER + '-' + Date.now();
  http.get('http://app:8000/search?q=' + q);
  http.get('http://app:8000/downstream');
  sleep(0.05);
}
