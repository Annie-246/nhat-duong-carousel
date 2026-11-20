---
name: nhat-duong-carousel
description: Dựng bộ ảnh carousel Facebook 1080x1080 cho page "Nhật Dương – Xóa mù AI" theo template cam/lưới trắng (heading Inter Bold nền cam #E1825A, ảnh minh họa viền đen bo góc, bullet Inter Regular, chữ ký avatar ở đáy). Nhận nội dung dán vào hoặc link bài, tự chia slide, tự tìm ẢNH THẬT đúng chủ đề (ảnh chụp web/app thật, ảnh từ nguồn chính thức) nếu user chưa gửi ảnh, render PNG và xuất vào thư mục output theo tên "yy.mm.dd - nội dung bài". Dùng khi user nói "làm carousel", "làm carrousel", "làm ảnh carousel bài này", "dựng slide FB", dán một bài viết/list tool rồi bảo làm ảnh, gửi link bài kèm yêu cầu làm carousel, hoặc yêu cầu sửa/render lại một bộ carousel Nhật Dương đã dựng.
---

# Carousel Nhật Dương – Xóa mù AI

Nguồn gốc: `D:/Phương Thảo/MARKETING NHẬT DƯƠNG XMAI/10 - FB Post Carrousel/template.pdf` (13 trang).
Mọi số đo dưới đây đo trực tiếp từ PDF (trang 940.5pt → 1080px, hệ số 1.1483) và đã nằm sẵn trong
`assets/carousel.css`. **Không sửa các lớp cố định**; chỉ viết nội dung trong `.stage`.

Thư mục skill: `C:/Users/pthao/.claude/skills/nhat-duong-carousel/`
- `assets/carousel.css` — khung chuẩn (nền, vệt cam, chữ ký, 3 khối, các bố cục linh hoạt)
- `assets/template.html` — mẫu 5 kiểu slide, copy làm điểm xuất phát
- `scripts/render.py` — render PNG + tự soát lỗi bố cục
- `scripts/shot.py` — chụp màn hình web thật làm ảnh minh họa

## 1. Công thức thiết kế (đúc kết từ template)

**Khổ & nền.** Vuông 1080×1080. Nền trắng phủ lưới uốn lượn xám rất nhạt (`bg-grid.png`). Ba vệt
gradient mờ ở đáy: cam đậm góc dưới trái, hồng–đỏ + vàng nhạt góc dưới phải. Nửa trên luôn sạch,
màu dồn xuống đáy tạo "chân" cho slide.

**Màu.** Chỉ 3 màu: cam `#E1825A` (nền heading, viền/mũi tên ở slide bước), đen `#000` (chữ nội dung,
viền ảnh, chấm bullet), trắng (chữ heading, nền). Không thêm màu khác vào chữ.

**Font.** Inter (bản 18pt) cho mọi chữ nội dung; Mulish (thay Muli) chỉ cho chữ ký.

| Phần | Font | Cỡ (px @1080) | Vị trí / căn |
|---|---|---|---|
| Heading 1 `NN. Tên` | Inter Bold, trắng | 58 / dòng 73.5 | nền cam ôm sát chữ (pad 4px), x=61, y=92 |
| Heading 2 (câu lợi ích) | Inter Bold, trắng | 41.8 / dòng 53 | nền cam ôm sát chữ, cách H1 12px |
| Thân bài | Inter Regular, đen | 27.7 / dòng 38 | bullet chấm đen 8px ở x=88, chữ ở x=111 |
| Bước ngắn (slide setup) | Inter Bold, đen | 27.7 | bullet sát nhau, không dòng trống |
| Chữ ký | Mulish ExtraBold "Nhật Dương" + Regular "Xóa mù AI" | 20.8 | giữa dưới, avatar tròn 51px ở x=439,y=986 |

**Lề.** Trái 61px (heading) — chấm bullet thụt vào 27px, chữ bullet thụt 50px. Phải 60px. Vùng nội dung
y 92 → 930; dưới 930 dành cho chữ ký và vệt màu.

**Ảnh minh họa.** Viền đen 1.5px, bo góc 16px, nền trắng, căn giữa ngang. Rộng tối đa 958px.
Hai ảnh cạnh nhau cách 22px. Slide dạng bước: viền cam + mũi tên cam giữa hai ảnh.

**Khoảng cách (đo trên cả 12 trang mẫu, px @1080).**

| Khoảng | Giá trị |
|---|---|
| Mép trên → hộp H1 | 92 |
| Hộp H1 → hộp H2 | 13 (cố định mọi trang) |
| H2 → ảnh **=** ảnh → chữ | luôn **bằng nhau**; mặc định 40, cho phép 27–50 |
| Chiều cao khối ảnh | 400–450 (tối thiểu 300) |
| Giữa 2 bullet | 1 dòng trống = 38 |
| Chữ cuối → avatar | 49–174, trung vị 61 (vùng nội dung kết thúc ở y=930) |
| Slide bước: H2 → list đậm | 26; list → ảnh: 49 |

`render.py` tự áp nhịp này: bó khối ảnh sát ảnh, chia chỗ thừa đều cho 2 khoảng (tối đa 50), ảnh bị ép
< 380px thì siết khoảng còn 30. Nó in `gaps a/b | visual h | free bottom` cho từng slide và báo WARN khi
2 khoảng lệch nhau, ngoài 27–50, ảnh < 300px, hoặc thừa > 120px dưới chữ (slide trông trống).
Không tự gõ margin tay đè lên nhịp này.

**Nội dung từng slide.** Mỗi slide = 1 mục: `NN. Tên` (số 2 chữ số) + 1 câu lợi ích ngắn + 1–2 bullet
(bullet 1: nó là gì/làm được gì; bullet 2: dùng khi nào/vì sao hữu ích). Xưng "ae" với người đọc,
giọng gần gũi, không màu mè.

## 2. Bố cục linh hoạt — luôn đủ 3 khối

Mỗi slide **bắt buộc** có đủ 3 khối và mỗi khối phải tách bạch, mắt đọc được theo một đường:
1. **Heading** (`.head`): luôn ở trên cùng, góc trái.
2. **Minh họa** (`.visual`): ảnh thật, hai ảnh, ảnh → ảnh, hoặc bảng/thẻ cột.
3. **Nội dung** (`.text`): bullet hoặc đoạn văn.

Được đổi thứ tự khối 2–3, đặt cạnh nhau, dùng bảng, cột — miễn là đọc được ngay. Các kiểu có sẵn:

| Kiểu | Khi nào | Cách viết |
|---|---|---|
| A. Chuẩn | Mặc định, ảnh ngang | head → `.visual` 1 ảnh → `.text ul` |
| B. Hai ảnh | So sánh, 2 màn hình, ảnh vuông/dọc | `.visual.two` |
| C. Bước | Hướng dẫn cài/làm theo bước | head → `.text.tight` (bullet đậm) → `.visual.orange` ảnh + `svg.arrow` + ảnh |
| D. Chia đôi | Ảnh dọc, ảnh điện thoại | head → `.row` > `.visual` + `.text` |
| E. Bảng / thẻ | Nhiều tiêu chí, so sánh số liệu, 2–3 lựa chọn | `.visual.fixed` chứa `table.tbl` hoặc `.cols > .card` |
| F. Khối nội dung | Minh họa chính là nội dung: prompt, câu chat, cây thư mục, danh sách tool | `.visual.fixed` chứa `.prompt` (hộp cam), `.bubbles > .bubble`, `.panel.tree` (`.l1` thụt cấp), `.grid2 > .card` (`.t` tên + `.s` mô tả) |

Mô phỏng giao diện (trong `.visual.fixed`): `.win` (khung cửa sổ, `.win-bar` có 3 chấm + tiêu đề) chứa
`.cc` = khung chat Claude (`.cc-user` tin nhắn người dùng, `.cc-ai` trả lời có `img/logo/claude-mark.svg`,
`.cc-input` ô soạn tin có `.txt`, `.att` ảnh đính kèm, `.bar` nút gửi cam); hoặc `.xp-addr` + `.xp-head` +
`.xp-row` = File Explorer. `.tools > .tool` (`.lg` logo, `.nm` tên, `.rl` vai trò) = khay công cụ.
`.sb > figure > img + figcaption` = bảng storyboard nền tối.

Ảnh hai bên có chú thích: `<figure><img><div class="cap">…</div></figure>` trong `.visual`.

Luật chống rối mắt:
- Một slide chỉ một kiểu bố cục. Không trộn bảng + 2 ảnh + 4 bullet.
- Tối đa 3 bullet, mỗi bullet ≤ 3 dòng (~62 ký tự/dòng). Dài hơn → tách slide.
- H1 ≤ ~24 ký tự, H2 ≤ ~40 ký tự để mỗi cái nằm 1 dòng.
- Chọn kiểu theo **tỉ lệ ảnh**: ảnh ngang → A; ảnh vuông/dọc → B, C, D. Ảnh không được bé lọt thỏm.
- Slide ít nội dung (free bottom > 150px) → thêm class `mid` vào `.stage` để căn giữa dọc.
- Chữ không đè ảnh, không đè vệt màu chữ ký, không chữ trắng ngoài heading.

## 3. Quy trình

1. **Lấy nội dung.**
   - Dán chữ: dùng nguyên văn làm nguồn.
   - Link Facebook: dùng skill `anthropic-skills:fb-post-reader` để đọc bài + lấy ảnh trong bài. Link web khác: đọc trọn
     trang (WebFetch / agent `web-fetch`). Ghi lại ảnh có sẵn trong bài.
   - Không bịa thông tin ngoài nguồn. Thiếu dữ kiện thì giữ ít chữ, không đoán.
2. **Lên dàn slide** vào `slides.md` trong thư mục làm việc: mỗi slide ghi H1, H2, bullet, kiểu bố cục,
   ảnh dự định + nguồn. Rút gọn câu theo công thức mục 1, giữ đúng ý gốc.
3. **Tìm ảnh** theo mục 4. Lưu vào `img/NN-ten.png`.
4. **Viết `carousel.html`**: copy `assets/template.html`, giữ dòng `<link>` tới `carousel.css`, xóa các
   slide mẫu, viết mỗi slide một `<section class="slide"><div class="stage">…</div></section>`.
5. **Render & soát số:**
   `python -I "C:/Users/pthao/.claude/skills/nhat-duong-carousel/scripts/render.py" "<work>/carousel.html" "<work>/png"`
   Mọi dòng phải `OK`. `WARN` → sửa (rút chữ, đổi bố cục, đổi ảnh) rồi render lại.
6. **Soát bằng mắt**: mở từng PNG bằng Read. Checklist: 3 khối rõ ràng; heading không xuống dòng lạ;
   ảnh đúng nội dung, nét, không bị cắt mất phần quan trọng; dấu tiếng Việt đủ; chữ ký nguyên vẹn.
7. **Xuất** (mục 5) và báo user.

## 4. Ảnh minh họa — chỉ ảnh thật, đúng thứ đang nói

Thứ tự ưu tiên:
1. **Ảnh user gửi** hoặc **ảnh có trong bài/link** → dùng luôn, không tìm thêm (trừ khi thiếu cho một slide).
2. **Nói về website / tool / app** → chụp chính trang chính thức của tool đó:
   `python -I "C:/Users/pthao/.claude/skills/nhat-duong-carousel/scripts/shot.py" <url> "<work>/img/NN-ten.png"`
   (`--scroll N` để tới đúng phần tính năng, `--mobile` nếu cần ảnh dọc). Ưu tiên trang thể hiện đúng
   tính năng bullet đang nói (gallery, editor, bảng giá…), không chỉ trang chủ chung chung.
   Trang chặn bot / đòi đăng nhập → lấy ảnh chụp màn hình chính thức trên site, docs, blog, press kit
   của tool đó.
3. **Nói về người / sản phẩm vật lý / sự kiện / địa điểm** → ảnh từ nguồn chính thức (site/newsroom
   công ty, tài khoản chính chủ), Wikimedia Commons, hoặc báo uy tín. Tìm bằng WebSearch, tải về.
4. **Ý trừu tượng** (con số, xu hướng) → chụp bằng chứng thật: biểu đồ/bảng trong bài nguồn, trang tài
   liệu, bài đăng gốc. Không có gì thật để minh họa → dùng kiểu E (bảng/thẻ) bằng chính dữ liệu, hoặc hỏi user.

Cấm: ảnh AI tạo, ảnh stock chung chung, ảnh "na ná" (tool khác, phiên bản khác, người khác), logo đứng
một mình thay cho giao diện, ảnh có watermark.

`shot.py` thoát với `BLOCKED` khi gặp trang chặn bot/captcha/đăng nhập (vd coolors.co trả trang
Cloudflare) — khi đó **không** dùng ảnh đó, chuyển sang ảnh chính thức trên docs/blog/press kit.
Trang chủ tối, nhiều khoảng trống (vd hero chỉ có 1 dòng chữ) → cuộn tới phần có giao diện thật, hoặc
crop (Pillow) giữ đúng vùng giao diện, để ảnh đọc được ở cỡ 958px.

Kiểm từng ảnh trước khi dùng: mở bằng Read, xác nhận đúng chủ thể của slide; độ phân giải đủ
(render.py báo nếu phóng > 1.6 lần). Ghi `sources.md`: slide – file – URL nguồn – ảnh thể hiện gì.
Popup cookie/quảng cáo che giao diện → chụp lại sau khi cuộn hoặc crop bỏ (Pillow), không để lọt.

## 5. Đặt tên & nơi lưu

Ngày = ngày làm (yy.mm.dd). Tên bài = nội dung ngắn gọn, có dấu, không ký tự cấm của Windows.

- Thành phẩm: `D:/Phương Thảo/MARKETING NHẬT DƯƠNG XMAI/10 - FB Post Carrousel/output/yy.mm.dd - <nội dung bài>/slide-01.png …`
- File làm việc (html, img, slides.md, sources.md): `D:/Phương Thảo/MARKETING NHẬT DƯƠNG XMAI/10 - FB Post Carrousel/work/yy.mm.dd - <nội dung bài>/`
- Trùng tên đã có → thêm `(v2)`, không ghi đè bộ cũ.

Báo user theo mẫu, mỗi bài một dòng tiêu đề:

```
[yy.mm.dd - nội dung bài] — N slide
Thư mục: <đường dẫn output>
Ảnh: slide 01 chụp từ <url>; slide 02 ảnh trong bài gốc; …
```
