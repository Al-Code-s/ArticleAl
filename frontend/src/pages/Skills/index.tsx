import { useEffect, useState } from 'react';
import { Button, Card, Input, List, Space, Tag, message } from 'antd';
import apiClient from '@services/api/client';

type Skill = { key:string; name:string; description:string; output_format:string; instructions:string; default_instructions:string; is_customized:boolean };

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]); const [selected, setSelected] = useState<Skill>(); const [saving,setSaving]=useState(false);
  const load = async () => { const data = await apiClient.get('/skills') as unknown as Skill[]; setSkills(data); if (!selected && data[0]) setSelected(data[0]); };
  useEffect(()=>{load().catch(()=>message.error('加载 Skills 失败'));},[]);
  const save = async () => { if (!selected) return; setSaving(true); try { const updated=await apiClient.put(`/skills/${selected.key}`,{instructions:selected.instructions}) as unknown as Skill; setSkills(prev=>prev.map(s=>s.key===updated.key?updated:s)); setSelected(updated); message.success('Skill 已保存'); } catch { message.error('保存失败'); } finally {setSaving(false);} };
  const reset = async () => { if (!selected) return; const updated=await apiClient.delete(`/skills/${selected.key}`) as unknown as Skill; setSkills(prev=>prev.map(s=>s.key===updated.key?updated:s)); setSelected(updated); message.success('已恢复默认'); };
  return <div style={{display:'flex',gap:16,height:'100%'}}><Card title="我的 Skills" style={{width:280}}><List dataSource={skills} renderItem={s=><List.Item onClick={()=>setSelected(s)} style={{cursor:'pointer',background:selected?.key===s.key?'#f0f5ff':undefined,padding:12}}><Space direction="vertical"><b>{s.name}</b><span>{s.description}</span>{s.is_customized&&<Tag color="blue">已自定义</Tag>}</Space></List.Item>}/></Card>{selected&&<Card title={selected.name} style={{flex:1}} extra={<Space><Button onClick={reset}>恢复默认</Button><Button type="primary" loading={saving} onClick={save}>保存 Skill</Button></Space>}><p>{selected.description} 输出：{selected.output_format}</p><Input.TextArea value={selected.instructions} onChange={e=>setSelected({...selected,instructions:e.target.value})} autoSize={{minRows:24}} /></Card>}</div>;
}







