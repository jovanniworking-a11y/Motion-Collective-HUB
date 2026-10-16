import Production from './production';
import { requireChatGPTUser } from './chatgpt-auth';
export const dynamic = 'force-dynamic';
async function Workspace(){ await requireChatGPTUser('/'); return <Production/>; }
export default function Home(){ return <Workspace/>; }
