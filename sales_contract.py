from flask import Flask, request, send_file, render_template
import fitz, os, tempfile, requests
import textwrap

app = Flask(__name__, template_folder='views')




def wrap_text_lines(text: str, max_width: int, num_lines: int = 2):
    """
    Wraps text to a given max width (in characters) and returns the specified number of lines.

    :param text: The original text string
    :param max_width: Maximum characters per line before wrapping
    :param num_lines: Number of lines to return from the wrapped text
    :return: Tuple containing the requested lines (empty strings if not enough lines)
    """
    wrapped = textwrap.wrap(text, width=max_width)
    result = []
    for i in range(num_lines):
        result.append(wrapped[i] if i < len(wrapped) else "")
    return tuple(result)


@app.route("/")
def form():
    return render_template("sales_contract.html")

@app.route("/generate", methods=["POST"])
def generate():
    form_data = request.form
    vehicle_condition_line1, vehicle_condition_line2,  = wrap_text_lines(form_data.get("vehicle_condition", "Macus"), max_width=120)
    payment_terms_line1, payment_terms_line2,payment_terms_line3,payment_terms_line4,payment_terms_line5  = wrap_text_lines(form_data.get("payment_terms", "Payment"), max_width=120, num_lines=5)
    customer_support_line1, customer_support_line2 = wrap_text_lines(
        form_data.get(
            "customer_support",
            "For questions and support concerning the delivery of your vehicle(s), please contact Customer Support at cs@basworld.com or +31 413 75 42 50."
        ), 
        max_width=120
    )

    general_terms_line1, general_terms_line2 = wrap_text_lines(
        form_data.get("general_terms", "The General Terms and Conditions of Sale and Delivery of BAS World apply to this offer, you can review these at all times via"),
        max_width=120
    )
    replacements = {
        "19/06/2025": form_data.get("date", ""),
        "10004048": form_data.get("invoice_number", ""),
        "€ 114,305.00": form_data.get("price", ""),
        "Dion Schrijvers": form_data.get("", ""),
        "Sales person": form_data.get("", ""),
        "1st reg.": form_data.get("", ""),
        "01/01/2019": form_data.get("", ""),
        "Damon S.A.": form_data.get("buyer_name", ""),
        "Damon S.A":form_data.get("buyer_name", ""),
        "Kipselis 56": form_data.get("buyer_street", ""),
        "113 62, Athina, GR": form_data.get("buyer_address", ""),
        "damon.sa.office@gmail.com": form_data.get("buyer_email", ""),
        "+34637404711": form_data.get("buyer_phone", ""),
        "VAT GR094419799": form_data.get("buyer_vat", ""),
        # "BAS World B.V.": form_data.get("seller_name", ""),
        "Mac. Arthurweg 2": form_data.get("seller_street", ""),
        "5466 AP, Veghel, NL": form_data.get("seller_address", ""),
        "VAT  NL806859945B02": form_data.get("seller_vat", ""),
        "17103220": form_data.get("coc", ""),
        # "CIF, Piraeus, GR": form_data.get("delivery", ""),
        "1 x Delivery Check-up": form_data.get("delivery_checkup", ""),
        "1 x T2LF": form_data.get("delivery_checkup_line2", ""),
        "Claas Axion 950 C-Matic Cebis 4X4": form_data.get("vehicle_description", ""),
        "+31 (0)413 72 83 20": form_data.get("seller_phone", ""),
        "info@basworld.com": form_data.get("seller_email", ""),
        "www.basworld.com": form_data.get("seller_website", ""),
        "Veghel NL": form_data.get("veghel", ""),
        "70243465": form_data.get("seller_reg", ""),
        "Claas": form_data.get("vehicle_brand", ""),
        "Axion 950 C-Matic Cebis": form_data.get("vehicle_model", ""),
        "Vehicles are sold in the condition you accepted. No warranty applies unless a BAS World warranty package is purchased or a": vehicle_condition_line1,
        "factory warranty is applicable.": vehicle_condition_line2,
        "A down payment of": payment_terms_line1,
        "€10,000.00":"",
        "or full payment needs to be received before":"",
        "20/06/2025":"",
        ". Failure to do so may result in the":"",
        "unavailability of the chosen vehicle(s).": payment_terms_line2, 
        "A full payment must be completed before": payment_terms_line3,
        "03/07/2025": "",
        ".": "",
        "In case the payment terms are not met, the order will be cancelled. We will charge you a cancellation fee of 10% and any": payment_terms_line4,
        "fee of 10% and any": "",
        "advance costs incurred, with a minimum of €2500. The vehicle(s) remains property of BAS World.": "",
        "Purchased vehicle(s) must be collected within 21 days. If this time frame is exceeded, a storage fee of €35 will be charged per": payment_terms_line5,
        "day for each vehicle.": "",

        # "Purchased vehicle(s) must be collected within 21 days. If this time frame is exceeded, a storage fee of €35 will be charged per": payment_terms_4_line1,
        # "day for each vehicle.": payment_terms_4_line2,
        "For questions and support concerning the delivery of your vehicle(s), please contact Customer Support at cs@basworld.com or": customer_support_line1,
        "+31 413 75 42 50.": customer_support_line2,
        "Vehicles are sold in the condition you accepted. No warranty applies unless a BAS World warranty package is purchased or a": vehicle_condition_line1,
        "factory warranty is applicable.": vehicle_condition_line2,


        "The General Terms and Conditions of Sale and Delivery of BAS World apply to this offer, you can review these at all times via": general_terms_line1,
        "https://basgroup.a.bigcontent.io/v1/static/General Terms and Conditions of Sale and Delivery of BAS World. By signing this": general_terms_line2,
    }


    # account_name = form_data.get("account_name", "")
    # found_account_name = False
    input_file = "Sales_Contract.pdf"
    roboto_regular = os.path.join("fonts", "Roboto.ttf")
    roboto_black = os.path.join("fonts", "RobotoBlack.ttf")
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    doc = fitz.open(input_file)
    cm_to_points = 72 / 2.54
    width_points = 10 * cm_to_points
    height_points = 3 * cm_to_points
    logo_rect = fitz.Rect(20, 20, 20 + width_points, 20 + height_points)
    first_page = doc[0]
    first_page.draw_rect(logo_rect, color=None, fill=(1, 1, 1))
    logo_url = form_data.get("logo") or "https://www.mascus.com/_next/static/media/logo.2f34c914.png"
    response = requests.get(logo_url)
    if response.status_code == 200:
        logo_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        logo_temp.write(response.content)
        logo_temp.close()
        first_page.insert_image(logo_rect, filename=logo_temp.name)
        os.unlink(logo_temp.name)
    bas_count = 0
    space_x = 0.3 / 2.54 * 72
    space_y = -0.05 / 2.54 * 72
    shift_total_x = 2 / 2.54 * 72
    color_gray = (153/255, 154/255, 167/255)
    veghel_color = (116/255, 116/255, 116/255)
    for page in doc:
        text_dict = page.get_text("dict")
        for block in reversed(text_dict["blocks"]):
            if block["type"] != 0:  # Skip non-text blocks
                continue
    
            if "lines" in reversed(block):
                for line in reversed(block["lines"]):
                    print(f"\n")

                    for span in reversed(line["spans"]):
                        
                        original_text = span["text"].strip()
                        print(f"Processing text: {original_text}")
                        for old_text, new_text in list(replacements.items()):
                                
                            # print(f"Checking if '{original_text}' matches '{old_text}'")
                            # print(original_text == old_text)
                            if original_text == old_text:
                                rect = fitz.Rect(span["bbox"])
                                font_size = span["size"]
                                if old_text == "70243465":
                                    page.draw_rect(rect, color=None, fill=(1, 1, 1))
                                    page.insert_text(
                                        (rect.x0, rect.y1 - 0.5),
                                        new_text,
                                        fontfile=roboto_regular,
                                        fontsize=font_size,
                                        color=(0, 0, 0)
                                    )
                                    # if not found_account_name:
                                    #     label_color = (124/255, 124/255, 124/255)
                                    #     page.insert_text(
                                    #         (rect.x0, rect.y1 + font_size + 7),
                                    #         "Account Name",
                                    #         fontfile=roboto_regular,
                                    #         fontsize=font_size,
                                    #         color=label_color
                                    #     )
                                        # if account_name:
                                        #     page.insert_text(
                                        #         (rect.x0, rect.y1 + (font_size * 2) + 12),
                                        #         account_name,
                                        #         fontfile=roboto_regular,
                                        #         fontsize=font_size,
                                        #         color=(0, 0, 0)
                                        #     )
                                        # found_account_name = True
                                    # continue
                                if old_text == "BAS World B.V.":
                                    bas_count += 1
                                    if bas_count == 3:
                                        erase_height = 15  # adjust if needed to cover NL + flag
                                        page.draw_rect(
                                            fitz.Rect(rect.x0, rect.y0, rect.x1 + 100, rect.y1 + erase_height),
                                            color=None,
                                            fill=(1, 1, 1)
                                        )
                                        continue
                                    elif bas_count == 2:
                                        page.draw_rect(rect, color=None, fill=(232/255, 232/255, 232/255))
                                        font_path = roboto_black
                                    else:
                                        page.draw_rect(rect, color=None, fill=(1, 1, 1))
                                        font_path = roboto_regular
                                    page.insert_text(
                                        (rect.x0, rect.y1 - 0.5),
                                        new_text,
                                        fontfile=font_path,
                                        fontsize=font_size,
                                        color=(0, 0, 0)
                                    )
                                    continue
                                if old_text == "Veghel NL":
                                    page.draw_rect(rect, color=None, fill=(232/255, 232/255, 232/255))
                                    page.insert_text(
                                        (rect.x0, rect.y1 - 0.5),
                                        new_text,
                                        fontfile=roboto_regular,
                                        fontsize=font_size,
                                        color=veghel_color
                                    )
                                    continue
                                if old_text == "Total":
                                    text_width = fitz.get_text_length(new_text, fontfile=roboto_black, fontsize=font_size)
                                    rect_expanded = fitz.Rect(rect.x0, rect.y0, rect.x0 + text_width + 10, rect.y1)
                                    page.draw_rect(rect_expanded, color=None, fill=(1, 1, 1))
                                    page.insert_text(
                                        (rect.x0 + shift_total_x, rect.y1 - 0.5),
                                        new_text,
                                        fontfile=roboto_black,
                                        fontsize=font_size,
                                        color=(0, 0, 0)
                                    )
                                    continue
                                if old_text == "www.basworld.com":
                                    page.draw_rect(rect, color=None, fill=(1, 1, 1))
                                    bigger_size = font_size - 1.7
                                    page.insert_text(
                                        (rect.x0, rect.y1 - 0.5),
                                        new_text,
                                        fontfile=roboto_regular,
                                        fontsize=bigger_size,
                                        color=color_gray
                                    )
                                    continue
                                if old_text in ["info@basworld.com", "+31 (0)413 72 83 20"]:
                                    page.draw_rect(rect, color=None, fill=(1, 1, 1))
                                    page.insert_text(
                                        (rect.x0, rect.y1 - 0.5),
                                        new_text,
                                        fontfile=roboto_regular,
                                        fontsize=font_size,
                                        color=color_gray
                                    )
                                    continue
                                if old_text in ["19/06/2025", "10004048"]:
                                    page.draw_rect(rect, color=None, fill=(1, 1, 1))
                                    page.insert_text(
                                        (rect.x0 + space_x, rect.y1 - 0.5 + space_y),
                                        new_text,
                                        fontfile=roboto_regular,
                                        fontsize=font_size,
                                        color=(0, 0, 0)
                                    )
                                    continue
                                page.draw_rect(rect, color=None, fill=(1, 1, 1))
                                page.insert_text(
                                    (rect.x0, rect.y1 - 0.5),
                                    new_text,
                                    fontfile=roboto_regular,
                                    fontsize=font_size,
                                    color=(0, 0, 0)
                                )
    doc.save(output_file)
    doc.close()
    return send_file(output_file, as_attachment=True, download_name="Updated.pdf")

if __name__ == "__main__":
    app.run(debug=True)
