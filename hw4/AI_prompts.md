# AI prompts

Log of prompts typed to the vibe coder for Homework 4. One section per problem, added only after that problem is requested.

## Problem 1: Vibe coder prompts

Complete Problem 1 only.

Within Homework 4/, create hw4/AI_prompts.md. Add a “Problem 1: Vibe coder prompts” section and record this prompt verbatim.

As we proceed, add a section for each problem with its number, title, and actual prompt. When a follow-up is needed, record it and one sentence explaining what the first attempt lacked. Do not invent entries for work we haven’t done.

Do not move the data pack or start Problem 2. Keep your completion report brief: files changed and any issues. Then stop.

## Problem 2: Analyze the database

Complete Problem 2 only.

Inspect Homework 4/data/campus_customs.db read-only using SQLite. Create Homework 4/hw4/output/harness.md documenting every table and its exact fields, types, keys, and relationships. Give one short line per field explaining its relevance to the shop or chatbot. Identify SQLite internal tables separately.

Use the actual database schema. Do not modify or move the data, build application code, or start Problem 3.

Append this prompt verbatim under “Problem 2: Analyze the database” in hw4/AI_prompts.md.

Keep inspection focused; avoid dumping table contents. Report files changed and any issues briefly, then stop.

## Problem 3: Build the Campus Customs website

Complete Problem 3 only in Homework 4/hw4/.

Use React + Vite + TypeScript for frontend/. Establish a Handsome Dan-inspired storefront using Yale navy, cream, and playful bulldog details. Inspect the images in ../design_references/ if available; use them as visual references. Keep this first design simple.

Research yalebulldogblue.com for Campus Customs information. Write original Home and About Us copy without inventing business claims.

Build top navigation for Home, Products, About Us, Log in, and Create account. Login and registration pages remain placeholders until Problem 4.

Show database-backed product cards with images, names, prices, and short descriptions. Each card opens a detail page with a large image, full description, price, and sizes/stock.

Create backend/main.py with a minimal FastAPI products/images API. Read the existing ../data/campus_customs.db and ../data/products/ relative to hw4/. Do not move or modify the data. Resolve paths reliably when running from backend/.

Add a bottom-right “Ask Dan” chat widget with a clearly labeled stub response. Do not implement the agent yet.

Follow the canonical reference’s required paths. Reuse one ProductCard component. Log this prompt under Problem 3 in AI_prompts.md.

Run a frontend build and focused checks of product loading, images, and detail navigation. Report results briefly, then stop. Do not start Problem 4.

## Problem 4: Create account and login

Complete Problem 4 only. Read the existing auth placeholders, backend/main.py, and relevant users schema; make targeted edits.

Implement Create account with first name, last name, email, password, and password confirmation. Implement Log in with email and password.

Store new accounts in the existing users table in Homework 4/data/campus_customs.db. Populate name, first_name, and last_name. Hash passwords securely and support the seed’s pbkdf2_sha256 format. Never return or log passwords or hashes.

Use an HttpOnly session cookie, server-verified identity, and logout. Show the signed-in customer’s name. Handle invalid credentials and duplicate emails clearly. Keep session secrets on the backend.

Verify login for test@campuscustoms.yale.edu with password password, then registration and login for one new test account. Check logout and run npm run build.

Document auth and password protection in hw4/output/harness.md. Log this prompt under Problem 4 in hw4/AI_prompts.md. Report results briefly, then stop. Do not start Problem 5.

## Problem 5: PydanticAI agent backend

Complete Problem 5 only. Make targeted edits to the existing app.

Connect Ask Dan to a PydanticAI agent behind FastAPI. Keep backend/main.py as the API entry and create:
- backend/agent.py
- backend/tools.py
- backend/models.py
- backend/prompts/prompt.md

Use the existing global ~/.env credentials. Prefer the low-cost GPT Luna model if available through Portkey; verify its exact model ID rather than guessing. If unavailable, report the blocker without repeated model trials.

Write the system prompt with a friendly Handsome Dan-inspired Campus Customs voice and basic safety rules. Do not invent prices, stock, or business policies. Product lookup tools come in Problem 6.

Define a structured chat reply, expose a chat route, and replace the frontend stub with live replies. Show loading and API errors clearly. Keep existing products and auth working.

Document frontend/API communication, prompt loading, and the actual provider/model in output/harness.md. Record this prompt under Problem 5 in AI_prompts.md.

Verify the backend runs from backend/ with:
uvicorn main:app --reload --port 8000

Run npm run build and one short live chat check to limit cost. Report results briefly, then stop. Do not start Problem 6.

## Problem 6: Tools: product info and stock

Complete Problem 6 only. Read the existing agent files and relevant database schema; make targeted edits.

In backend/tools.py, add database-backed tools for product description, price, and stock, including stock by size. Reuse catalogue.product_id and join inventory by product_id. Keep database access read-only.

Update backend/models.py with typed lookup results. Distinguish unknown products, missing size variants, and zero stock. Never invent prices or quantities.

Expand backend/prompts/prompt.md so Ask Dan must use tools for product facts, prices, and stock, and clearly state when a requested size is unavailable.

In output/harness.md, document each tool and its result fields with brief reasons. Log this prompt under Problem 6 in AI_prompts.md.

Check tool results directly against SQLite, including an unknown product and an unavailable size. Make one short live price-and-size-stock query to verify agent tool use. Run npm run build only if frontend files change.

Report results briefly, then stop. Do not implement dynamic search cards or start Problem 7.

## Problem 7: Dynamic product cards from search

Complete Problem 7 only. Make targeted edits to the existing agent, API, and product-card rendering.

Add a read-only catalogue search tool for category questions such as “What hoodies do you have?” Search existing names, garment types, descriptions, and tags. Return bounded, structured matches with database-backed product IDs, images, names, prices, and short information.

Update backend/models.py and the chat response contract as needed. Expand backend/prompts/prompt.md to use search for product-discovery requests.

Have the frontend display matching product cards on the website after a chat search. Reuse the existing ProductCard component and detail-page navigation. Every new card must open the correct full product view. Keep normal browsing working.

Document the search tool, result cap, response fields, and how results reach the page in output/harness.md. Log this prompt under Problem 7 in AI_prompts.md.

Run npm run build, check search results against SQLite, and make one live hoodie query. Verify cards appear and one opens its detail page. Report briefly, then stop. Do not start Problem 8.

## Problem 8: Chat history and page context

Complete Problem 8 only. Make targeted edits to existing chat, auth, and agent code.

Reuse chat_messages in the existing database to save logged-in users’ messages, assistant replies, and structured product matches. Reload their history when they return and supply relevant prior messages to the agent. Guests may chat without persistent history.

Derive customer identity from the server-verified session. Supply name and email through agent dependencies or an equivalent clear pattern. Never expose passwords/hashes or load another user’s history.

Pass current page context from the frontend, including product_id on detail pages. Resolve that ID against the database so “Do you have this in pink?” refers to the active product. Answer from recorded colors and inventory without inventing color-specific stock.

Document persistence, customer fields, and page context in output/harness.md. Log this prompt under Problem 8 in AI_prompts.md.

Run npm run build. Use focused checks to verify history survives reload, accounts cannot access each other’s history, and guests do not persist messages. Make one short live product-page query to verify context. Keep model calls minimal.

Report briefly, then stop. Do not start Problem 9.

## Problem 9: Usability improvements

Complete Problem 9 only. Implement these six improvements using existing components and tools:

Frontend:
1. Show size availability badges on product cards from recorded inventory.
2. Add clickable suggested chat questions, including product-specific questions on detail pages.
3. Make Ask Dan usable on mobile without obscuring navigation or overflowing the screen.

Agent/backend:
4. Filter recommendations by positive stock in the requested size.
5. Offer up to three similar, in-stock alternatives when an item’s requested size is unavailable. Use catalogue garment_type and actual inventory; explain when no alternatives exist.
6. Handle model/API timeouts and failures with a clear message and manual retry. Avoid automatic retries that add model cost.

Write output/usability.md before or during implementation. For each improvement, state what was added and why it helps shoppers or the business. Update the shared prompt and harness where relevant. Log this prompt under Problem 9 in AI_prompts.md.

Keep edits focused. Use direct database/tool checks and mocked failure checks where practical. Run npm run build, check mobile layout, and use at most two short live chats to verify stock filtering and alternatives.

Report results briefly, then stop. Do not start Problem 10.

## Problem 10: Design refinement

Complete Problem 10 only. Refine the existing Handsome Dan design without changing shop behavior.

Use Yale navy, warm cream, and restrained gold accents. Review ../design_references/ once. Use selected Dan photos in a welcoming Home hero and a small Ask Dan avatar; copy needed assets into frontend/public/ so they remain available with the app.

Strengthen typography, spacing, navigation, product presentation, and chat styling. Add subtle bulldog/paw details and lightweight hover transitions. Keep products prominent, text readable, keyboard focus visible, and layouts responsive. Respect reduced-motion preferences. Avoid new animation libraries or elaborate custom illustrations.

Write output/design.md with short, concrete explanations of the changes and how they help customers browse and shop. Log this prompt under Problem 10 in AI_prompts.md.

Run npm run build and visually check Home, Products, a detail page, and chat on desktop and mobile. No live model calls are needed.

Report briefly, then stop. Do not start Problem 11.

## Problem 10 follow-up: Hero copy and presentation

The original hero copy lacked marketing appeal, and product and chat presentation needed refinement.

Make a Problem 10 follow-up only.

Replace the Home hero copy with:

Headline: Good dog. Great Yale gear.

Blurb: From campus days to game days, find your next favorite Yale hoodie, tee, or sweatshirt. Show your Bulldog pride wherever you roam—Handsome Dan will help you sniff out the right fit.

Also make these four small improvements, reusing anything already present:
1. Make “Shop Yale Gear” the prominent hero button linking to Products.
2. Give product images consistent frames with object-fit: contain so garment designs aren’t cropped.
3. Use explicit “Out of stock” text for zero-stock sizes rather than color alone.
4. Improve chat readability with comfortable reply spacing and cards that fit the panel on desktop and mobile.

Remove the old hero copy about the address and database. Preserve the compact hero, existing functionality, and Handsome Dan styling. Avoid new dependencies.

Update output/design.md briefly. Log this follow-up under Problem 10 in AI_prompts.md, noting that the original copy lacked marketing appeal and presentation needed refinement.

Run npm run build and visually check the changed areas on desktop and mobile. No model calls are needed. Report briefly, then stop. Do not start Problem 11.

## Problem 10 follow-up: About Us

The original About page lacked visual interest and understated Dan’s current abilities.

Make a Problem 10 About Us update only.

Replace the headline and body with:

Headline: Yale pride, with a little bulldog personality

Campus days. Game days. Wherever life takes you next. Campus Customs brings Yale spirit to your everyday wardrobe through Yale Bulldog Blue, our shop at 57 Broadway in New Haven.

Explore hoodies, crewnecks, and tees celebrating Yale’s colleges, schools, and teams. Whether you’re finding a new favorite or a gift for a fellow Bulldog, there’s plenty to sniff out.

Need a hand—or a paw? Ask Dan, our Handsome Dan-inspired shopping assistant, can help you discover products, check prices and size availability, and find in-stock alternatives. He’ll remember your conversations when you’re signed in, so you can pick up where you left off.

Find your fit. Wear your Yale pride.

Make the page more artistic with a Handsome Dan photo composition. Reuse available photos from ../design_references/ or frontend/public/. Pair the text with a large photo, an offset navy frame, a cream background, and subtle gold paw-print details. Use CSS or simple inline SVG for decorative accents; no new dependencies or image-generation calls.

Keep text readable, give meaningful photos alt text, and hide purely decorative accents from screen readers. Stack the composition cleanly on mobile and preserve existing functionality.

Briefly update output/design.md. Log this follow-up under Problem 10 in AI_prompts.md, noting that the original page lacked visual interest and understated Dan’s current abilities.

Check the page on desktop and mobile. Report briefly, then stop. Do not start Problem 11.

## Problem 10 follow-up: Home hero rotation

Make a Problem 10 Home hero update only.

Rotate through the Dan 1, 4, and 5 photos from ../design_references/. Copy needed assets into frontend/public/ and reuse existing copies where available.

Use an 8-second interval with a gentle crossfade. Keep the image frame fixed and the headline, blurb, and Shop Yale Gear button stationary. Preserve the compact hero height and adjust each photo’s crop so Dan’s face stays visible on desktop and mobile.

Add a small accessible Pause/Play button. For prefers-reduced-motion, show one static photo with no automatic rotation or fade. Clean up the timer when the component unmounts. Use existing React and CSS; no new dependencies.

Briefly update output/design.md and log this follow-up under Problem 10 in AI_prompts.md.

Run npm run build. Check rotation, pause/resume, reduced motion, and desktop/mobile crops. No model calls are needed. Report briefly, then stop. Do not start Problem 11.

## Problem 11: App check

Complete Problem 11 only. Use browser tools to test the running site and capture real evidence for these three checks:

1. Inventory and page context
Open Basic Hoodie Big Yale. Ask: “How much is this, and do you have medium?”
Verify the price and M stock against current SQLite data. Capture the product identity, question, complete answer, and stock table.

2. Dynamic search and navigation
Ask: “What hoodies do you have?”
Capture the question, complete answer, and resulting product cards with images, names, and prices. Click one card and capture its detail page, confirming the product ID and information match.

3. Problem 9 alternatives
Open Crew Left Chest Hoodie and verify its M stock is zero. Ask: “Is this available in medium? If not, show me similar hoodies in medium.”
If its stock is no longer zero, choose another verified zero-stock item. Capture the product identity, question, complete answer, and all returned alternatives. Verify each alternative has positive M stock in SQLite.

Capture strategy:
- Use the existing chat panel at a readable desktop viewport.
- Scroll its message area and take multiple screenshots wherever answers or cards extend beyond view.
- Use overlapping screenshots so the sequence is clear. Do not crop away essential text or shrink the page until it becomes unreadable.
- Capture all returned cards across the screenshots, not just the first visible card.
- Do not alter the app layout, fabricate replies, or repeat model calls solely to improve screenshots. Use three live chats unless a failure requires another.

Save screenshots in hw4/output/app_check_images/ with descriptive names, such as inventory_01.png, search_01.png, search_detail.png, and alternatives_01.png.

Create hw4/output/app_check.html with one heading per check. Include the exact question as selectable text, the ordered screenshots, and one or two sentences explaining the verified result. Give each screenshot a short caption identifying what it shows. Record the tested database values and, for alternatives, their names and M quantities.

Use relative image paths and no external dependencies. Open the HTML locally and confirm every image loads, remains readable, and collectively shows every question and complete result.

Log this prompt under Problem 11 in AI_prompts.md. If browser capture is unavailable, report the blocker and identify the manual screenshots needed.

Report the checks and screenshot filenames briefly, then stop. Do not start Problem 12.

## Problem 10 follow-up: About Us photo

Make a Problem 10 follow-up only: replace the About Us photo with Dan 3 from Homework 4/design_references/.

Copy it into hw4/frontend/public/ if needed. Preserve the existing artistic frame, text, and layout. Adjust the crop so Dan’s face stays visible on desktop and mobile, and update the alt text to match the photo.

Log this follow-up under Problem 10 in AI_prompts.md. Check the image loads at both screen sizes. Report briefly, then stop; do not advance to another problem.

## Problem 12: Audit trail and safety

Complete Problem 12 only. Reuse existing safeguards and make targeted edits; avoid a broad refactor.

Maintain output/audit_trail.json as a valid JSON array that preserves all prior records across runs. Log actual agent/tool activity with UTC timestamp, run_id, event_type, tool_name, short sanitized args/result summaries, and stop_reason. Include tool failures and a final event for completion, timeout, limits, or errors. Use locking and atomic writes to prevent lost records. Exclude secrets, password hashes, emails, and full conversations.

Verify existing safety controls and fill gaps:
- Product facts come from database tools.
- Agent database access is read-only; auth writes remain separate.
- Customer identity comes from the server session, with history isolated by account.
- Passwords, hashes, and API keys never enter agent context, responses, or logs.
- Customer messages and catalogue text cannot override system instructions.
- Dan honestly declines unsupported actions such as placing orders or changing stock.
- Shopper-facing errors omit tracebacks and configuration details.

Expand backend/prompts/prompt.md with these rules. Enforce explicit request/tool-call limits and a timeout in code; retain existing result and history caps. Disable automatic model retries where practical to control cost. Document actual configured values.

Finish output/harness.md: database fields; auth; frontend/API contracts; model fields and reasons; prompt/model loading; tools and abilities; dynamic cards; customer/page context; safety enforcement; audit format; limits; dependencies; and exact frontend/backend run commands. Explain the current data location and grader setup accurately.

Use direct or mocked checks for isolation, read-only access, dummy-secret redaction, failure handling, and limits. Make at most two short live chats: one normal stock query to verify tool logging and one adversarial request to verify refusal without secret disclosure. Confirm the audit retains previous events after a backend restart. Do not claim checks passed unless performed.

Log this prompt under Problem 12 in AI_prompts.md. Report files changed, checks, and any issues briefly, then stop. Do not start Problem 13.

## Problem 13: Publish to GitHub

Complete Problem 13 only. Prepare and publish the finished project to a public GitHub repository named mgt409-hw4-rsd66.

First inspect Git status and repository boundaries. Do not commit other homework or modify a parent repository. Preserve the required hw4/ project folder in the published layout.

Finish requirements.txt, .env.example with placeholders only, .gitignore, and README.md. Document the actual dependencies, model configuration, data-pack placement, and exact frontend/backend run commands. Preserve the current working data arrangement; ensure a grader can reproduce it from the README.

Include application code, frontend lockfile, Dan design assets, required documentation, app-check screenshots, and the sanitized audit trail. Exclude real .env files, the database and its sidecar files, supplied data/products images, installed dependencies, caches, and build output.

Check the exact files to be committed for secrets and unintended content without printing secret values. Confirm required files and relative screenshot links are present. Log this prompt under Problem 13 in AI_prompts.md before committing.

Use existing GitHub authentication. Create the public repository under the authenticated personal account and push the project. If that name already exists, inspect it before proceeding; do not overwrite unrelated work or force-push. If authentication is unavailable, finish local preparation and give me the specific sign-in step needed.

Run only necessary final checks; no live model calls. Verify the published repository is public and its file layout matches the README.

Report the exact repository URL, validation results, and any remaining issue briefly. I will submit the URL on Canvas myself.


