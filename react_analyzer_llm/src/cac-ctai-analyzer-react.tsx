import React, { useState, useEffect } from 'react';
import { PlusCircle, Trash2, Send, Copy } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const lungLobes = ['左上叶', '左下叶', '右上叶', '右中叶', '右下叶'];
const noduleTypes = ['实性', '混合型', '磨玻璃'];
const langRadsLevels = ['1类', '2类', '3类', '4类','4A类','4B类','4X类', '5类','6类'];

const NoduleInput = ({ nodule, onChange, onRemove }) => (
    <div className="space-y-2 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <Select value={nodule.location} onValueChange={(value) => onChange('location', value)}>
                <SelectTrigger>
                    <SelectValue placeholder="选择位置" />
                </SelectTrigger>
                <SelectContent>
                    {lungLobes.map((lobe) => (
                        <SelectItem key={lobe} value={lobe}>{lobe}</SelectItem>
                    ))}
                </SelectContent>
            </Select>
            <Select value={nodule.type} onValueChange={(value) => onChange('type', value)}>
                <SelectTrigger>
                    <SelectValue placeholder="选择类型" />
                </SelectTrigger>
                <SelectContent>
                    {noduleTypes.map((type) => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                    ))}
                </SelectContent>
            </Select>
            <Select value={nodule.langRads} onValueChange={(value) => onChange('langRads', value)}>
                <SelectTrigger>
                    <SelectValue placeholder="Lang-RADS分级" />
                </SelectTrigger>
                <SelectContent>
                    {langRadsLevels.map((level) => (
                        <SelectItem key={level} value={level}>{level}</SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <Input type="number" placeholder="长直径 (mm)" value={nodule.size} onChange={(e) => onChange('size', e.target.value)} step="0.1" />
            <Input type="number" placeholder="风险 (%)" value={nodule.risk} onChange={(e) => onChange('risk', e.target.value)} min="0" max="100" step="0.1" />
        </div>
        <Button variant="destructive" size="icon" onClick={onRemove}><Trash2 className="h-4 w-4" /></Button>
    </div>
);

const CacCtaiAnalyzer = () => {
    const [cacScore, setCacScore] = useState('');
    const [nodules, setNodules] = useState([]);
    const [analysis, setAnalysis] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [patientName, setPatientName] = useState('');
    const [error, setError] = useState('');
    const [clientIp, setClientIp] = useState('');

    useEffect(() => {
        fetch('https://api.ipify.org?format=json')
            .then(response => response.json())
            .then(data => setClientIp(data.ip))
            .catch(error => console.error('Error fetching IP:', error));
    }, []);

    const addNodule = () => {
        setNodules([...nodules, { location: '', size: '', type: '', risk: '', langRads: '' }]);
    };

    const updateNodule = (index, field, value) => {
        const updatedNodules = [...nodules];
        updatedNodules[index] = { ...updatedNodules[index], [field]: value };
        setNodules(updatedNodules);
    };

    const removeNodule = (index) => {
        setNodules(nodules.filter((_, i) => i !== index));
    };

    const validateForm = () => {
        if (!patientName.trim()) {
            setError('请输入患者姓名');
            return false;
        }
        if (!cacScore.trim()) {
            setError('请输入CAC个数');
            return false;
        }
        if (nodules.length === 0) {
            setError('请至少添加一个CTAI结节');
            return false;
        }
        for (let i = 0; i < nodules.length; i++) {
            const nodule = nodules[i];
            if (!nodule.location || !nodule.type || !nodule.size || !nodule.risk || !nodule.langRads) {
                setError(`请填写结节 ${i + 1} 的所有信息`);
                return false;
            }
        }
        setError('');
        return true;
    };

    const generateId = () => {
        const randomNum = Math.floor(Math.random() * 1000000);
        return `${clientIp}-${randomNum}`;
    };

    const submitData = async () => {
        if (!validateForm()) {
            return;
        }

        setIsLoading(true);
        setAnalysis('');

        const apiData = {
            ID: generateId(),
            Name: patientName,
            CAC: parseInt(cacScore),
            CTAI: {}
        };

        nodules.forEach((nodule, index) => {
            apiData.CTAI[`item${index + 1}`] = {
                NoduleScore: parseFloat(nodule.risk) / 100,
                NoduleType: nodule.type,
                NoduleSize: parseFloat(nodule.size),
                NoduleLocation: nodule.location,
                NoduleLangRads: nodule.langRads
            };
        });

        try {
            const response = await fetch("http://120.238.255.78:8005/explain_chat", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(apiData)
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                const parts = text.split('{');
                if (parts.length > 1) {
                    const jsonPart = '{' + parts[parts.length - 1];
                    try {
                        const jsonResponse = JSON.parse(jsonPart);
                        setAnalysis(prev => prev + jsonResponse.response);
                    } catch (e) {
                        console.error("Error parsing JSON:", e);
                    }
                }
            }
        } catch (error) {
            console.error("Error calling API:", error);
            setError("发生错误，请稍后再试。");
        }

        setIsLoading(false);
    };

    const copyAnalysis = () => {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(analysis)
                .then(() => {
                    alert('分析结果已复制到剪贴板');
                })
                .catch(err => {
                    console.error('复制失败: ', err);
                    fallbackCopyTextToClipboard(analysis);
                });
        } else {
            fallbackCopyTextToClipboard(analysis);
        }
    };

    const fallbackCopyTextToClipboard = (text) => {
        const textArea = document.createElement("textarea");
        textArea.value = text;

        // Avoid scrolling to bottom
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.position = "fixed";

        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            const successful = document.execCommand('copy');
            const msg = successful ? '分析结果已复制到剪贴板' : '复制失败，请手动复制';
            alert(msg);
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
            alert('复制失败，请手动复制');
        }

        document.body.removeChild(textArea);
    };

    return (
        <div className="max-w-full md:max-w-4xl mx-auto p-4 space-y-4">
            <Card className="w-full">
                <CardHeader>
                    <CardTitle>CAC和CTAI报告分析器</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="patientName">患者姓名</Label>
                            <Input id="patientName" value={patientName} onChange={(e) => setPatientName(e.target.value)} placeholder="输入患者姓名" />
                        </div>
                        <div>
                            <Label htmlFor="cacScore">CAC数量</Label>
                            <Input id="cacScore" type="number" value={cacScore} onChange={(e) => setCacScore(e.target.value)} placeholder="输入CAC数量" />
                        </div>
                    </div>
                    <div>
                        <Label>CTAI结节信息</Label>
                        <br/>
                        {nodules.map((nodule, index) => (
                            <NoduleInput
                                key={index}
                                nodule={nodule}
                                onChange={(field, value) => updateNodule(index, field, value)}
                                onRemove={() => removeNodule(index)}
                            />
                        ))}
                        <Button onClick={addNodule} className="mt-2"><PlusCircle className="mr-2 h-4 w-4" /> 添加结节</Button>
                    </div>
                </CardContent>
                <CardFooter>
                    <Button onClick={submitData} disabled={isLoading} className="w-full">
                        {isLoading ? '分析中...' : <><Send className="mr-2 h-4 w-4" /> 提交分析</>}
                    </Button>
                </CardFooter>
            </Card>
            {error && (
                <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}
            {analysis && (
                <Card className="w-full">
                    <CardHeader>
                        <CardTitle className="flex justify-between items-center">
                            分析结果
                            <Button onClick={copyAnalysis} variant="outline" size="sm">
                                <Copy className="mr-2 h-4 w-4" /> 复制结果
                            </Button>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                            <pre className="long-text">{analysis}</pre>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default CacCtaiAnalyzer;