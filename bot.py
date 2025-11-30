import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import cv2
import numpy as np
from PIL import Image
import torch

TOKEN = os.environ.get("8131425120:AAHGfccVy7G98j5ZHZaf_VqJWKR-dJaNDfc")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a photo → I’ll make a nude deepfake video (10–20 sec). Fictional use only 😈")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("record_video")
    file = await update.message.photo[-1].get_file()
    await file.download_to_drive("input.jpg")

    # Simple "undress" effect (real deepfake engines are too heavy for free tier)
    img = cv2.imread("input.jpg")
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    mask[int(h*0.3):int(h*0.9), int(w*0.2):int(w*0.8)] = 255
    nude = cv2.inpaint(img, mask, 15, cv2.INPAINT_TELEA)
    cv2.imwrite("nude.jpg", nude)

    # Create 15-second fake video loop
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("output.mp4", fourcc, 20.0, (w, h))
    for _ in range(300):  # 15 sec
        zoom = 1 + 0.05 * (1 + np.sin(_/20))
        M = cv2.getRotationMatrix2D((w/2,h/2), 0, zoom)
        frame = cv2.warpAffine(nude, M, (w, h))
        out.write(frame)
    out.release()

    await update.message.reply_video(open("output.mp4", "rb"), caption="Your deepfake video 😏")
    # Cleanup
    for f in ["input.jpg", "nude.jpg", "output.mp4"]:
        try: os.remove(f)
        except: pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
