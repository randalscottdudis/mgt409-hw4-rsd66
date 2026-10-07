# Usability

Six shopper-facing improvements for Campus Customs. Each one uses the catalogue and inventory already on the site.

## 1. Size badges on product cards

Product cards show each recorded size. A size with quantity above zero stays readable. A recorded quantity of zero is marked out of stock. Sizes that are not in `inventory` are not shown.

Shoppers can see whether a size is on hand before opening the product. The shop avoids a click that ends in a surprise stockout.

## 2. Suggested chat questions

Ask Dan shows short questions the shopper can click. On a product page those questions use “this,” so they refer to the open product. Elsewhere they ask about categories, a size, or a known price.

A click starts the question, which helps someone who is not sure what to type. Product-page prompts keep the conversation on the item they are already viewing.

## 3. Ask Dan on a small screen

On a narrow screen the panel stays within the viewport, scrolls inside the message list, and leaves the top navigation usable. The launcher stays at the bottom instead of covering the menu.

Shoppers on a phone can ask a question and still reach Home, Products, and About.

## 4. Recommendations limited to positive stock

When a shopper names a size, catalogue search keeps only products whose recorded quantity for that size is greater than zero. A missing size and a quantity of zero are both left out.

The cards Dan shows are items that can actually be sold in the requested size, so the shop does not recommend a stockout.

## 5. Similar in-stock alternatives

If the requested size of one product is not available, Dan can offer up to three other products of the same `garment_type` that have that size in stock. If none do, he says so.

Shoppers get a next step instead of a dead end, and the suggestion is another real item of the same kind.

## 6. Timeouts and failures, with manual retry

A model timeout or other API failure returns a short message. The server does not send the question again. The chat panel keeps the question and offers Retry.

The shopper stays in control, and a failure does not spend another model call by itself.
