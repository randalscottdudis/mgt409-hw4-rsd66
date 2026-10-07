# Design

Visual refinements for the Campus Customs storefront. Shop behavior, routes, and catalogue data are unchanged.

## Color and type

The page uses Yale navy `#00356b`, warm cream `#f6f1e7`, and a thin gold `#b0893e` line. Body text is slightly larger, with a serif for headings and a plain sans for reading. Prices stay navy so the number is easy to scan next to the product name.

## Home hero

The home hero keeps a compact 4:5 frame. The headline, blurb, and “Shop Yale Gear” button stay put while three Handsome Dan photos crossfade every 8 seconds: the campus steps photo already in `frontend/public/dan-hero.jpeg`, the field photo copied to `dan-field.jpg`, and the porch photo copied to `dan-5.avif`. Each crop keeps Dan’s face in the frame. A Pause/Play control stops and resumes the rotation. When the shopper prefers reduced motion, the hero shows the steps photo only, with no timer and no fade. On a narrow screen the same frame stacks under the copy.

## Navigation

The sticky navy bar has a gold bottom edge and larger link targets. The current page is a cream pill. Other links lighten on hover. Keyboard focus uses a gold outline on links, buttons, and fields.

## Products

Each product photo sits in a square cream frame with `object-fit: contain`, so the garment design stays whole. Cards still show the name, price, short description, and size badges. A zero-stock size includes the words “Out of stock”, so availability is readable without relying on color. A light lift on hover separates the card under the pointer. When the shopper prefers reduced motion, that lift and the other transitions stay still.

## About Us

The About page uses the headline “Yale pride, with a little bulldog personality” and explains the Broadway shop, the catalogue, and what Ask Dan can do: find products, check prices and sizes, suggest in-stock alternatives, and remember a signed-in conversation. The illustrated Dan 3 photo (`frontend/public/dan-3.jpg`) sits beside the copy in an offset navy frame, cropped so the face stays in view, on the cream page, with two gold paw marks that are hidden from screen readers. On a narrow screen the photo stacks under the text.

## Ask Dan

The launcher and the chat header use a small portrait, `frontend/public/dan-avatar.jpg`, so Dan is recognizable without covering the products. Replies have more space between them and a looser line height. Product cards inside a reply wrap to the panel width, and each chat photo uses a shorter frame so the name stays with the garment. When cards are open, the panel stays below the navigation and the conversation scrolls inside it. The panel header is navy with cream type, and the close control stays cream so it remains readable. The panel still sits below the navigation on a phone.
