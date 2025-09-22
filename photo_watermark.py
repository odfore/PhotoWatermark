#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
from datetime import datetime


def get_exif_data(image_path):
    """
    从图片中提取EXIF数据
    
    Args:
        image_path (str): 图片文件路径
        
    Returns:
        dict: EXIF数据字典，如果出错则返回None
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            print(f"错误: 文件不存在: {image_path}")
            return None
            
        # 检查文件是否为图片格式
        valid_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
        if not image_path.lower().endswith(valid_extensions):
            print(f"警告: 文件可能不是支持的图片格式: {image_path}")
        
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data is not None:
            return {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
        else:
            print(f"警告: 图片不包含EXIF数据: {image_path}")
    except Exception as e:
        print(f"读取EXIF数据时出错: {e}")
        return None
    return None


def extract_datetime(exif_data):
    """
    从EXIF数据中提取拍摄时间
    
    Args:
        exif_data (dict): EXIF数据字典
        
    Returns:
        str: 格式化的日期字符串，如果无法提取则返回None
    """
    if not exif_data:
        return None
    
    # 尝试获取拍摄时间的不同字段
    datetime_keys = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
    datetime_str = None
    
    for key in datetime_keys:
        if key in exif_data and exif_data[key]:
            datetime_str = exif_data[key]
            break
    
    if datetime_str:
        try:
            # 解析时间字符串
            # 处理不同的时间格式
            formats = ['%Y:%m:%d %H:%M:%S', '%Y/%m/%d %H:%M:%S']
            for fmt in formats:
                try:
                    dt = datetime.strptime(datetime_str, fmt)
                    # 返回年月日格式
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except Exception as e:
            print(f"解析时间字符串时出错: {e}")
    return None



def create_watermark_text(image_path):
    """
    为图片创建水印文本
    
    Args:
        image_path (str): 图片文件路径
        
    Returns:
        str: 水印文本
    """
    # 首先尝试从EXIF数据获取时间
    exif_data = get_exif_data(image_path)
    if exif_data:
        date_text = extract_datetime(exif_data)
        if date_text:
            return date_text
    
    # 如果无法获取EXIF时间信息，则使用文件修改时间
    try:
        if os.path.exists(image_path):
            mtime = os.path.getmtime(image_path)
            mdate = datetime.fromtimestamp(mtime)
            return mdate.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"获取文件修改时间时出错: {e}")
    
    # 如果都无法获取时间，则返回默认文本
    return "Unknown Date"


def get_font(font_size):
    """
    获取系统字体
    
    Args:
        font_size (int): 字体大小
        
    Returns:
        ImageFont: 字体对象
    """
    try:
        # 首先尝试使用PIL的默认字体加载方法，它会自动查找系统字体
        return ImageFont.load_default().font_variant(size=font_size)
    except Exception:
        pass
    
    # 尝试使用系统字体
    font_paths = [
        "/System/Library/Fonts/Arial.ttf",  # macOS
        "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"  # Linux alternative
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"加载字体 {font_path} 时出错: {e}")
            continue
    
    # 如果所有字体都失败，则使用默认字体，但给出警告
    print(f"警告: 无法加载系统字体，将使用默认字体。指定的字体大小 {font_size} 将被忽略。")
    return ImageFont.load_default()


def add_watermark(image_path, output_path, watermark_text, font_size=40, 
                  font_color=(255, 255, 255), position='bottom-right', opacity=128):
    """
    在图片上添加水印
    
    Args:
        image_path (str): 原始图片路径
        output_path (str): 输出图片路径
        watermark_text (str): 水印文本
        font_size (int): 字体大小
        font_color (tuple): 字体颜色 (R, G, B)
        position (str): 水印位置
        opacity (int): 水印透明度 (0-255)
    """
    try:
        # 打开图片
        image = Image.open(image_path)
        
        # 如果图片不是RGBA模式，转换为RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        width, height = image.size
        
        # 创建水印图层
        watermark_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 获取字体
        font = get_font(font_size)
        
        # 计算文本尺寸
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 检查文本是否超出图片尺寸
        if text_width > width or text_height > height:
            print(f"警告: 水印文本尺寸({text_width}x{text_height})可能超出图片尺寸({width}x{height})")
        
        # 根据位置参数确定水印位置
        margin = 10
        if position == 'top-left':
            x, y = margin, margin
        elif position == 'top-right':
            x, y = width - text_width - margin, margin
        elif position == 'bottom-left':
            x, y = margin, height - text_height - margin
        elif position == 'center':
            x, y = (width - text_width) // 2, (height - text_height) // 2
        else:  # 默认为右下角
            x, y = width - text_width - margin, height - text_height - margin
        
        # 调整颜色透明度
        r, g, b = font_color
        adjusted_color = (r, g, b, opacity)
        
        # 绘制水印
        draw.text((x, y), watermark_text, font=font, fill=adjusted_color)
        
        # 合并图层
        watermarked_image = Image.alpha_composite(image, watermark_layer)
        
        # 转换为RGB模式以保存为JPEG等格式
        watermarked_image = watermarked_image.convert('RGB')
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存图片
        watermarked_image.save(output_path, quality=95)
        print(f"水印已添加并保存到: {output_path}")
        
    except Exception as e:
        print(f"添加水印时出错: {e}")
        raise


def process_image(image_path, font_size, font_color, position, opacity):
    """
    处理单个图片
    
    Args:
        image_path (str): 图片文件路径
        font_size (int): 字体大小
        font_color (tuple): 字体颜色 (R, G, B)
        position (str): 水印位置
        opacity (int): 水印透明度
    """
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在: {image_path}")
        return False
    
    # 获取水印文本
    watermark_text = create_watermark_text(image_path)
    print(f"使用水印文本: {watermark_text}")
    
    # 确定输出目录
    dir_name = os.path.dirname(image_path)
    file_name = os.path.basename(image_path)
    name, ext = os.path.splitext(file_name)
    
    # 创建_watermark子目录
    watermark_dir = os.path.join(dir_name, f"{name}_watermark")
    
    # 确定输出文件路径
    output_path = os.path.join(watermark_dir, file_name)
    
    # 添加水印
    try:
        add_watermark(image_path, output_path, watermark_text, font_size, font_color, position, opacity)
        return True
    except Exception as e:
        print(f"处理图片时出错: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='为图片添加时间水印')
    parser.add_argument('image_path', help='图片文件路径')
    parser.add_argument('-s', '--font-size', type=int, default=40, help='字体大小 (默认: 40)')
    parser.add_argument('-c', '--font-color', nargs=3, type=int, default=[255, 255, 255], 
                        help='字体颜色 RGB值 (默认: 255 255 255)')
    parser.add_argument('-p', '--position', 
                        choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                        default='bottom-right', help='水印位置 (默认: bottom-right)')
    parser.add_argument('-o', '--opacity', type=int, default=128, 
                        help='水印透明度 0-255 (默认: 128)')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.font_size <= 0:
        print("错误: 字体大小必须大于0")
        return
    
    if not all(0 <= c <= 255 for c in args.font_color):
        print("错误: 字体颜色值必须在0-255之间")
        return
        
    if not 0 <= args.opacity <= 255:
        print("错误: 透明度值必须在0-255之间")
        return
    
    # 解析颜色参数
    font_color = tuple(args.font_color)
    
    # 处理图片
    success = process_image(args.image_path, args.font_size, font_color, args.position, args.opacity)
    
    if success:
        print("处理完成")
    else:
        print("处理失败")
        sys.exit(1)


if __name__ == '__main__':
    main()