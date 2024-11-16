import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import streamlit as st
from matplotlib import font_manager


min_version_number = st.sidebar.number_input(
    'Mininum version number',
    min_value=1,
    max_value=40,
    value=1,
)
qr_size_cm = st.sidebar.number_input(
    'QR size (cm)',
    min_value=1,
    max_value=5,
    value=5,
)
n_rows = st.sidebar.number_input(
    'Layout number of rows',
    min_value=1,
    max_value=5,
    value=3,
)
n_cols = st.sidebar.number_input(
    'Layout number of columns',
    min_value=1,
    max_value=5,
    value=2,
)
has_to_include_order_number = st.sidebar.toggle('Include order number')
replicate_number = st.sidebar.number_input(
    'Replicate number',
    min_value=1,
    max_value=None,
    value=1,
)
fill_color = st.sidebar.color_picker(
    'Fill color',
    '#000000',
)
back_color = st.sidebar.color_picker(
    'Background color',
    '#FFFFFF',
)

st.title('QR code generator')
col1, col2 = st.columns([1, 2])
with col1:
    multiline_text_to_coded = st.text_area(
        'Text to be coded',
    )


imgs = []

text_to_coded_list = multiline_text_to_coded.split('\n')
qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=20,
    border=10
)
max_best_fit = 1
for text_to_coded in text_to_coded_list:
    qr.add_data(text_to_coded)
    max_best_fit = max(qr.best_fit(), max_best_fit)
    qr.clear()

qr = qrcode.QRCode(
    version=max(max_best_fit, min_version_number),
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=20,
    border=10
)

qr_images = []
for i, text_to_coded in enumerate(text_to_coded_list):
    if text_to_coded == "":
        continue
    qr.add_data(text_to_coded)
    qr.make()
    qr_images.append( (i, text_to_coded, qr.make_image(fill_color=fill_color, back_color=back_color)) )
    qr.clear()

output_data_list = []
for order_number, text_to_coded, img in qr_images:

    if has_to_include_order_number:
        text_to_print = f"{order_number+1} [{text_to_coded}]"
    else:
        text_to_print = f"[{text_to_coded}]"

    if replicate_number == 1:
        output_data_list.append( (text_to_print, img) )
    else:
        for j in range(replicate_number):
            output_data_list.append( (text_to_print + f" {j+1}", img) )

if len(qr_images) > 0:
    img = qr_images[0][2]
    resolution=img.box_size * img.width / qr_size_cm * 2.54
chunk_size = n_rows * n_cols

images_to_print = []
for chunk in (output_data_list[i:i+chunk_size] for i in range(0, len(output_data_list), chunk_size)):
    w, h = chunk[0][1].size
    dst = Image.new('RGB', (w * n_cols, h * n_rows), "#FFFFFF")
    d = ImageDraw.Draw(dst)
    try:
        font = ImageFont.truetype("NotoSansCJK-Regular.ttc", size=50)
    except OSError:
        font = ImageFont.load_default(size=50)
        #st.write(font_manager.findSystemFonts())
    for j, (text_to_print, img) in enumerate(chunk):
        x, y = (j % n_cols) * w, (j // n_cols) * h
        dst.paste(img, (x, y))
        d.text((x + 20, y + 10), text_to_print, "black", font=font, anchor="la")

    for i in range(n_cols):
        if i == 0:
            continue
        d.line(((w*i, 0), (w*i, dst.size[1])), fill_color,  5)
    for i in range(n_rows):
        if i == 0:
            continue
        d.line(((0, h*i), (dst.size[0], h*i)), fill_color, 5)

    images_to_print.append(dst)


with col2:

    # for debugging information
    #st.write(f"{img.box_size * img.width / qr_size_cm} pixels / cm" )
    #st.write(f"{img.box_size * img.width / qr_size_cm * 2.54} pixels / inch" )
    pdf_buf = io.BytesIO()
    for img in images_to_print:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(buf)

        img.save(pdf_buf, format="PDF", resolution=resolution)

if len(images_to_print) > 0:
    img = images_to_print[0]

    col1.write(f"pdf size: {img.size[0] / resolution * 2.54:.2f}cm x {img.size[1] / resolution * 2.54:.2f}cm" )
    col1.download_button(
        label="Download PDF",
        data=pdf_buf,
        file_name="out.pdf",
        mime="application/pdf",
    )