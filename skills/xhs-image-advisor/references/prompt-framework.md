# 8维度Prompt框架

生成小红书配图时，从8个维度构建prompt：

## 维度说明

### 1. 主体（Subject）
画面核心内容
- 产品：护肤品瓶子、化妆品、服装...
- 人物：博主展示、手部特写...
- 场景：餐桌、书桌、卧室...

### 2. 场景（Scene）
拍摄环境/背景
- 室内：卧室、浴室、客厅
- 室外：咖啡店、公园、街拍
- 纯色背景：白色、米色、灰色

### 3. 光线（Lighting）
- 自然光：阳光、窗边
- 灯光：暖光、冷光、柔光
- 氛围光：日落、逆光

### 4. 角度（Angle）
- 俯拍：适合产品平铺
- 平拍：适合人物展示
- 侧拍：适合立体展示
- 特写：突出细节

### 5. 风格（Style）
- 清新：干净、明亮
- 复古：胶片感、暖色调
- 高级：简约、质感
- 可爱：粉色系、软萌

### 6. 色调（Color）
- 暖色：橙、黄、粉
- 冷色：蓝、绿、紫
- 莫兰迪：低饱和、高级灰
- 黑白：极简、质感

### 7. 构图（Composition）
- 居中：主体突出
- 三分：平衡美感
- 留白：高级感
- 满版：信息量大

### 8. 氛围（Mood）
- 温馨：家、生活感
- 活力：青春、动感
- 专业：信任感
- 松弛：舒适、惬意

## Prompt模板

```
[主体], [场景], [光线], [角度], [风格], [色调], [构图], [氛围], 
high quality, detailed, suitable for Xiaohongshu, 
vertical format 3:4
```

## 示例

### 护肤品封面
```
skincare bottle on white marble table, 
minimalist bathroom scene, 
soft natural light from window, 
top-down angle, 
clean and fresh style, 
soft pink and white tones, 
centered composition with negative space, 
serene and premium mood,
high quality, detailed, suitable for Xiaohongshu,
vertical format 3:4
```

### 穿搭展示
```
fashion outfit flat lay on beige background,
bedroom scene,
warm natural light,
top-down angle,
chic and modern style,
earth tones and neutrals,
rule of thirds composition,
effortless and stylish mood,
high quality, detailed, suitable for Xiaohongshu,
vertical format 3:4
```

### 美食探店
```
delicious food dish on wooden table,
cozy cafe interior,
warm ambient lighting,
45-degree angle,
food photography style,
warm orange and brown tones,
shallow depth of field,
appetizing and inviting mood,
high quality, detailed, suitable for Xiaohongshu,
vertical format 3:4
```
