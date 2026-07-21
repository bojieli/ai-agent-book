# Hiểu sâu về AI Agent: Nguyên lý thiết kế và thực hành kỹ thuật

**[中文](README.md) · [English](README.en.md) · Tiếng Việt ← hiện tại · [தமிழ்](README.ta.md)**

Kho này là kho mã nguồn mở chính thức của cuốn sách *Hiểu sâu về AI Agent: Nguyên lý thiết kế và thực hành kỹ thuật*, bao gồm **toàn bộ nội dung sách** và **mã ví dụ đi kèm**. Toàn bộ bản thảo, hình minh họa và mã thí nghiệm đều được mở nguồn; hoan nghênh bạn tự chạy các thí nghiệm, gửi issue và PR.

## 📖 Sách điện tử

Mã nguồn của bản dịch tiếng Việt (do [@toanalien](https://github.com/toanalien) đóng góp) nằm trong thư mục [`book-vi/`](book-vi/). Bản
gốc tiếng Trung ở [`book/`](book/), bản tiếng Anh ở [`book-en/`](book-en/) và
bản Tamil ở [`book-ta/`](book-ta/).

- **Mã nguồn tiếng Việt**: `book-vi/introduction.vi.md` (lời mở đầu),
  `book-vi/chapter1.vi.md` ~ `book-vi/chapter10.vi.md` (chương 1 đến chương 10),
  `book-vi/afterword.vi.md` (lời bạt)
- **Bản PDF đã biên dịch**: [PDF tiếng Việt](book-vi/AI-Agents-in-Depth-Bojie-Li-v1.2-vi.pdf) · [PDF bản gốc tiếng Trung](book/%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3-AI-Agent-%E6%9D%8E%E5%8D%9A%E6%9D%B0-v1.2.pdf)
- **Tự biên dịch**: sau khi cài pandoc, xelatex, lớp tài liệu ElegantBook và các phông chữ liên quan, chạy

  ```bash
  cd book-vi && bash build_pdf.sh
  ```

  Hình tiếng Việt nằm trong `book-vi/images/`; chi tiết dàn trang nằm trong
  `book-vi/preamble.tex` và `book-vi/*.lua`.

## 📑 Tổng quan nội dung (Chương 1–10)

Toàn bộ sách xoay quanh công thức cốt lõi **Agent = LLM + context + tools**. Nội dung mười chương như sau:

- **Chương 1 · Kiến thức nền tảng về Agent**: xuất phát từ mô hình mới “model as Agent”, xây dựng công thức cốt lõi **Agent = LLM + context + tools**, đồng thời giới thiệu kỹ thuật Harness — mọi năng lực kỹ thuật nằm ngoài mô hình mới là lợi thế cạnh tranh thực sự.
- **Chương 2 · Kỹ thuật ngữ cảnh**: ngữ cảnh quyết định trần năng lực của Agent. Đi sâu vào cấu trúc ngữ cảnh của API mô hình lớn, thiết kế thân thiện với KV Cache, prompt engineering, prompt động và Agent Skills, siêu thông tin trên thanh trạng thái, cũng như các chiến lược nén ngữ cảnh.
- **Chương 3 · Bộ nhớ người dùng và kho tri thức**: giúp Agent ghi nhớ người dùng qua nhiều phiên và kết nối với tri thức bên ngoài. Bao gồm hệ thống bộ nhớ người dùng, pipeline RAG cơ bản, cũng như tổ chức và truy xuất tri thức vượt ra ngoài văn bản phẳng (chỉ mục cấu trúc, đồ thị tri thức, v.v.).
- **Chương 4 · Công cụ**: công cụ là đôi tay của Agent. Trình bày phân loại công cụ và nguyên tắc thiết kế tổng quát, giao thức MCP và thách thức chọn công cụ, ba loại công cụ cảm nhận/thực thi/cộng tác, cũng như Agent bất đồng bộ hướng sự kiện.
- **Chương 5 · Coding Agent và sinh mã**: mã là “công cụ có thể tạo ra công cụ mới”, là siêu năng lực của Agent tổng quát. Lấy Coding Agent cấp sản xuất làm ví dụ để trình bày triển khai đầy đủ của công cụ tổng quát mạnh nhất này.
- **Chương 6 · Đánh giá Agent**: biến biểu hiện của Agent thành tín hiệu có thể so sánh. Từ môi trường đánh giá, thiết kế bộ dữ liệu, hệ thống chỉ số, đến ý nghĩa thống kê, observability, chọn mô hình dựa trên đánh giá, cho tới đánh giá nội bộ và môi trường mô phỏng cấp sản xuất.
- **Chương 7 · Hậu huấn luyện mô hình**: toàn cảnh ba giai đoạn tiền huấn luyện, SFT và RL. Khi nào chọn SFT, khi nào chọn RL, RLHF, so sánh thuật toán, dữ liệu và môi trường, cũng như các hướng tiên phong giúp mô hình học cách gọi công cụ và nâng cao hiệu quả mẫu.
- **Chương 8 · Tự tiến hóa của Agent**: Agent vẫn có thể trưởng thành mà không cần sửa trọng số. Ba mô thức học tập: học từ kinh nghiệm, chủ động phát hiện công cụ, và từ “người dùng công cụ” thành “người tạo công cụ”, giúp Agent đi từ “thông minh” tới “thành thạo”.
- **Chương 9 · Đa phương thức và tương tác thời gian thực**: mở rộng cảm nhận và hành động từ văn bản sang giọng nói, GUI và thế giới vật lý. Ba mô thức giọng nói (pipeline nối tầng/đa phương thức đầu cuối/full-duplex), cảm nhận và tổng hợp giọng nói dạng streaming, Computer Use và thao tác robot.
- **Chương 10 · Cộng tác đa Agent**: trí tuệ tập thể có thể cao hơn cá thể. Khung phân loại đa Agent, khi nào thực sự tốt hơn đơn Agent, cộng tác chia sẻ và không chia sẻ ngữ cảnh, các chế độ thất bại, cũng như “xã hội Agent” nổi lên.

## 💻 Mã đi kèm

Tất cả dự án được tổ chức theo **chương**, tương ứng một-một với mười chương của sách, bao phủ lộ trình học hoàn chỉnh từ khái niệm cơ bản đến kỹ thuật nâng cao. Thư mục có dạng `chapterN/tên-dự-án/`. Phần lớn thí nghiệm của chương 5, 8, 9 và 10 hiện đã có demo đi kèm có thể chạy độc lập, và đã được kiểm chứng chạy thông qua API LLM thực.

### Giải thích loại dự án

Các dự án đi kèm được chia thành ba loại; hãy đối chiếu biểu tượng bên dưới để biết mức độ “chạy ngay” của từng dự án:

- ✅ **Có thể chạy độc lập**: kho này tự chứa mã đầy đủ; cấu hình API Key (xem cuối tài liệu) là có thể chạy.
- 📖 **Hướng dẫn tái hiện**: bản thân dự án là tài liệu tái hiện chi tiết; các phụ thuộc là **kho bên ngoài** cần tự `git clone` (framework huấn luyện, benchmark đánh giá, v.v.), xem mục “Lấy kho bên ngoài” bên dưới.
- 🚧 **Tài liệu thiết kế**: hiện chỉ chứa kiến trúc và phương án triển khai; mã có thể chạy vẫn đang được hoàn thiện.

Các dự án sau **không phải** loại ✅ có thể chạy độc lập; hãy lưu ý khi clone kho này:

| Dự án | Loại | Mô tả |
| --- | --- | --- |
| `chapter7/AdaptThink` · `AWorld-train` · `MiniMind-pretrain` · `retool` · `SpatialReasoning` | 📖 Hướng dẫn tái hiện | Thí nghiệm huấn luyện, phụ thuộc framework bên ngoài, tái hiện theo README |
| Toàn bộ benchmark chương 6 · đa số framework huấn luyện chương 7 · chương 9 `browser-use`/`claude-quickstarts` · chương 10 `use-computer-while-calling` | 📖 Hướng dẫn tái hiện | Phụ thuộc kho bên ngoài, xem “Lấy kho bên ngoài” |

### Lấy kho bên ngoài (tóm tắt)

Một **phần** thí nghiệm ở chương 6, 7, 9 và 10 phụ thuộc vào benchmark đánh giá, framework huấn luyện, nền tảng robot và các **kho bên ngoài** khác (không được tích hợp vào kho này vì lý do dung lượng và bản quyền). Để tránh quá tải thông tin ngay từ đầu, **lệnh clone đầy đủ, địa chỉ upstream và commit đã được sách kiểm chứng nằm ở cuối tài liệu, trong mục “Phụ lục · Lấy kho bên ngoài”**. Khuyến nghị bắt đầu với các dự án có thể chạy độc lập ở các chương trước; khi cần tái hiện thí nghiệm huấn luyện / đánh giá / robot, hãy làm theo chỉ dẫn cuối tài liệu.

## 🚀 Chương 1 · Kiến thức nền tảng về Agent

### learning-from-experience - So sánh học tăng cường và LLM
`chapter1/learning-from-experience/`

So sánh học tăng cường truyền thống (Q-learning) với học trong ngữ cảnh dựa trên LLM, tái hiện các insight then chốt trong bài viết “The Second Half” của Shunyu Yao. Thông qua trò chơi săn kho báu, dự án cho thấy LLM có thể vượt RL truyền thống về hiệu quả mẫu tới 250–400 lần.

**Khái niệm cốt lõi**: học tăng cường, học trong ngữ cảnh, hiệu quả mẫu, tri thức tiên nghiệm

### web-search-agent - Mô hình Kimi K2 như một Agent
`chapter1/web-search-agent/`

Triển khai Agent có khả năng tìm kiếm chuyên sâu cơ bản, có thể tìm kiếm nhiều vòng và tổng hợp thông tin.

**Khái niệm cốt lõi**: tìm kiếm web, Agent nguyên sinh từ mô hình

### search-codegen - Tích hợp công cụ nguyên sinh với GPT-5
`chapter1/search-codegen/`

Xây dựng Agent có năng lực tìm kiếm chuyên sâu cơ bản và sandbox chạy mã, tổng hợp sử dụng tìm kiếm web, thực thi mã và các công cụ khác để phân tích phức tạp.

**Khái niệm cốt lõi**: tìm kiếm web, sinh mã, Agent nguyên sinh từ mô hình

### context - Nghiên cứu ablation về ngữ cảnh
`chapter1/context/`

Thông qua thí nghiệm ablation có hệ thống để cho thấy tầm quan trọng của từng thành phần trong ngữ cảnh Agent. Hỗ trợ nhiều nhà cung cấp LLM (SiliconFlow Qwen, ByteDance Doubao, Moonshot Kimi), cấu hình các chế độ ngữ cảnh khác nhau để quan sát thay đổi hành vi của Agent.

**Khái niệm cốt lõi**: quản lý ngữ cảnh, gọi công cụ, vòng lặp ReAct, nghiên cứu ablation

## 🎯 Chương 2 · Kỹ thuật ngữ cảnh

### local_llm_serving - Triển khai LLM cục bộ và gọi công cụ
`chapter2/local_llm_serving/`

Giải pháp triển khai LLM cục bộ đa nền tảng, tự động chọn backend tối ưu (vLLM hoặc Ollama). Cho thấy ngay cả mô hình nhỏ 0.6B cũng có thể đạt năng lực gọi công cụ xuất sắc nhờ thiết kế hệ thống tốt. Hỗ trợ phản hồi streaming và hiển thị quá trình suy nghĩ theo thời gian thực.

**Khái niệm cốt lõi**: triển khai mô hình, Chat Template, xử lý streaming, gọi công cụ

### attention_visualization - Trực quan hóa cơ chế attention
`chapter2/attention_visualization/`

Trực quan hóa toàn bộ chuỗi token đầu vào/đầu ra và phân bố trọng số attention của LLM, giúp hiểu sâu cách mô hình xử lý ngữ cảnh, suy luận và gọi công cụ.

**Khái niệm cốt lõi**: cơ chế attention, phân tích token, trực quan hóa quá trình suy luận

### kv-cache - Thiết kế ngữ cảnh thân thiện với KV Cache
`chapter2/kv-cache/`

Khám phá ảnh hưởng của các chế độ quản lý ngữ cảnh khác nhau lên KV Cache, minh họa các mẫu sai phổ biến làm phá hỏng hiệu quả cache. Thông qua thí nghiệm, dự án cho thấy thiết kế ngữ cảnh đúng có thể giảm đáng kể độ trễ và chi phí.

**Khái niệm cốt lõi**: KV Cache, tối ưu ngữ cảnh, tối ưu hiệu năng

### context-compression - Policy nén ngữ cảnh
`chapter2/context-compression/`

Triển khai và so sánh nhiều chiến lược nén ngữ cảnh, bao gồm tóm tắt, trích xuất thông tin then chốt, nén ngữ nghĩa, v.v. Mục tiêu là giảm lượng token sử dụng trong khi vẫn giữ năng lực của Agent.

**Khái niệm cốt lõi**: nén ngữ cảnh, tối ưu token, mật độ thông tin

### prompt-engineering - Nghiên cứu ablation về prompt engineering
`chapter2/prompt-engineering/`

Mở rộng framework Tau-Bench, dùng thí nghiệm ablation có hệ thống để định lượng ảnh hưởng của các yếu tố prompt engineering khác nhau lên hiệu năng Agent. Cho thấy giọng điệu, tổ chức chỉ dẫn, mô tả công cụ và các yếu tố khác ảnh hưởng thế nào tới tỷ lệ hoàn thành nhiệm vụ.

**Khái niệm cốt lõi**: prompt engineering, nghiên cứu ablation, benchmark hiệu năng

### system-hint - Tối ưu system prompt
`chapter2/system-hint/`

Nghiên cứu ảnh hưởng của System Hint tới hành vi Agent, khám phá cách tối ưu system prompt để nâng cao hiệu năng.

**Khái niệm cốt lõi**: system prompt, dẫn hướng hành vi, tối ưu prompt

### log-sanitization - Xử lý khử nhạy cảm log
`chapter2/log-sanitization/`

Triển khai hệ thống khử nhạy cảm log thông minh, bảo vệ dữ liệu nhạy cảm trong khi vẫn giữ thông tin debug.

**Khái niệm cốt lõi**: bảo vệ quyền riêng tư, xử lý log, an toàn dữ liệu

### prompt-injection - Thí nghiệm tấn công/phòng thủ prompt injection
`chapter2/prompt-injection/`

Xây dựng thí nghiệm đối chứng với 3 kịch bản tấn công (tiêm trực tiếp, tiêm gián tiếp, tiêm qua bộ nhớ) × 4 cấu hình phòng thủ (không phòng thủ, gia cố prompt, đánh dấu nguồn, phòng thủ kết hợp), dùng quy tắc xác định để thống kê tỷ lệ tấn công thành công, trực quan cho thấy tỷ lệ tiêm lệnh giảm mạnh khi phòng thủ được chồng lớp.

**Khái niệm cốt lõi**: prompt injection, tiêm gián tiếp, tách dữ liệu và chỉ dẫn, kiểm tra runtime

### agent-skills-ppt - Tạo PPT bằng Agent Skills theo cơ chế tiết lộ tăng dần
`chapter2/agent-skills-ppt/`

Tái hiện tư tưởng “tiết lộ tăng dần” của Agent Skills: khi khởi động, Agent chỉ thấy một thư mục Skill mỏng; sau khi nhận diện nhiệm vụ cần Skill `pptx`, nó mới tải dần quy trình đầy đủ, tài liệu chi tiết và script đóng gói, cuối cùng dùng python-pptx tạo file `.pptx` thật.

**Khái niệm cốt lõi**: Agent Skills, tiết lộ tăng dần, tải theo nhu cầu, điều phối công cụ

## 📚 Chương 3 · Bộ nhớ người dùng và kho tri thức

### user-memory - Hệ thống bộ nhớ người dùng
`chapter3/user-memory/`

Xây dựng hệ thống bộ nhớ người dùng dài hạn, giúp Agent ghi nhớ sở thích và lịch sử tương tác của người dùng để cung cấp dịch vụ cá nhân hóa.

**Khái niệm cốt lõi**: bộ nhớ dài hạn, cá nhân hóa, mô hình hóa người dùng

### mem0 / memobase - Đối chiếu framework bộ nhớ mã nguồn mở
`chapter3/mem0/` và `chapter3/memobase/`

Dùng hai framework bộ nhớ mã nguồn mở mem0 và Memobase để triển khai hai phiên bản bộ nhớ người dùng, làm đối chứng cho thí nghiệm 3-2 “so sánh chiến lược bộ nhớ”, thuận tiện so sánh hình thái trích xuất và chất lượng trả lời của các phương án bộ nhớ khác nhau.

**Khái niệm cốt lõi**: framework bộ nhớ, mem0, Memobase, so sánh phương án

### user-memory-evaluation - Framework đánh giá bộ nhớ người dùng
`chapter3/user-memory-evaluation/`

Đánh giá có hệ thống độ chính xác, mức độ liên quan và hiệu quả của hệ thống bộ nhớ người dùng, bao gồm nhiều kịch bản kiểm thử và chỉ số đánh giá.

**Khái niệm cốt lõi**: framework đánh giá, test case, đo lường hiệu năng

### dense-embedding - Dịch vụ truy xuất vector embedding dày đặc
`chapter3/dense-embedding/`

Xây dựng dịch vụ tìm kiếm tương tự vector, so sánh hai thuật toán chỉ mục láng giềng gần đúng ANNOY (dựa trên cây) và HNSW (dựa trên đồ thị). Cho thấy sự đánh đổi giữa các chiến lược chỉ mục về hiệu năng, bộ nhớ và khả năng cập nhật.

**Khái niệm cốt lõi**: embedding dày đặc, truy xuất vector, thuật toán ANN, tìm kiếm ngữ nghĩa

### sparse-embedding - Công cụ truy xuất thưa
`chapter3/sparse-embedding/`

Triển khai từ đầu công cụ tìm kiếm vector thưa dựa trên thuật toán BM25; thông qua log phong phú và giao diện trực quan để hiển thị cơ chế bên trong của công cụ tìm kiếm, giúp hiểu cách tính trọng số tần suất từ và nguyên lý chỉ mục đảo.

**Khái niệm cốt lõi**: embedding thưa, BM25, TF-IDF, khớp chính xác

### retrieval-pipeline - Pipeline truy xuất lai
`chapter3/retrieval-pipeline/`

Xây dựng pipeline truy xuất hoàn chỉnh, kết hợp truy xuất dày đặc, truy xuất thưa và neural reranking. Thông qua các test case được thiết kế kỹ, dự án cho thấy hiệu quả bổ sung lẫn nhau của truy xuất lai trong các ngữ cảnh khác nhau.

**Khái niệm cốt lõi**: truy xuất lai, neural reranking, cross-encoder, hợp nhất truy xuất

### multimodal-agent - Trích xuất thông tin đa phương thức
`chapter3/multimodal-agent/`

So sánh ba chiến lược xử lý đa phương thức: xử lý đa phương thức nguyên sinh, trích xuất thành văn bản, và phân tích bằng công cụ. Thông qua nghiên cứu ablation trong một framework thống nhất, dự án làm rõ sự đánh đổi giữa các con đường kỹ thuật về độ trung thực, chi phí và tính linh hoạt.

**Khái niệm cốt lõi**: đa phương thức, hiểu hình ảnh, OCR, xử lý đầu cuối

### structured-index - Chỉ mục có cấu trúc
`chapter3/structured-index/`

Triển khai và so sánh hai chiến lược chỉ mục tiên tiến RAPTOR (cây trừu tượng đệ quy) và GraphRAG (đồ thị tri thức). Thông qua sổ tay kỹ thuật chỉ mục, dự án minh họa cách xây dựng chỉ mục có cấu trúc phản ánh tầng bậc và liên kết nội tại của tri thức.

**Khái niệm cốt lõi**: RAPTOR, GraphRAG, tóm tắt phân cấp, đồ thị tri thức

### agentic-rag - RAG tác nhân
`chapter3/agentic-rag/`

So sánh khác biệt hiệu năng giữa RAG truyền thống không tác nhân (Non-Agentic RAG) và Agentic RAG. Cho thấy Agent có thể chủ đạo truy xuất thông tin lặp bằng mô thức ReAct, từ đó nâng cao đáng kể chất lượng câu trả lời khi xử lý hỏi đáp tư pháp phức tạp.

**Khái niệm cốt lõi**: Agentic RAG, vòng lặp ReAct, truy xuất lặp, khám phá chủ động

### agentic-rag-for-user-memory - Xây dựng bộ nhớ người dùng bằng Agentic RAG
`chapter3/agentic-rag-for-user-memory/`

Áp dụng framework Agentic RAG vào quản lý lịch sử hội thoại người dùng; thông qua khả năng tìm kiếm lặp nhiều vòng để xử lý truy xuất bộ nhớ xuyên phiên, hiện thực năng lực hồi tưởng cơ bản và truy xuất đa phiên.

**Khái niệm cốt lõi**: bộ nhớ người dùng, chỉ mục lịch sử hội thoại, truy xuất xuyên phiên

### contextual-retrieval - Truy xuất nhận biết ngữ cảnh
`chapter3/contextual-retrieval/`

Triển khai kỹ thuật truy xuất nhận biết ngữ cảnh do Anthropic đề xuất: sinh phần tóm tắt tiền tố chứa ngữ cảnh cốt lõi cho từng khối văn bản, giải quyết vấn đề mất ngữ cảnh của phương pháp chia khối truyền thống, giảm tỷ lệ truy xuất thất bại 49–67%.

**Khái niệm cốt lõi**: tăng cường ngữ cảnh, sinh tiền tố, neo ngữ nghĩa, tối ưu truy xuất

### contextual-retrieval-for-user-memory - Hệ thống bộ nhớ người dùng nhận biết ngữ cảnh
`chapter3/contextual-retrieval-for-user-memory/`

Áp dụng kỹ thuật truy xuất nhận biết ngữ cảnh vào xây dựng bộ nhớ người dùng, kết hợp Advanced JSON Cards và RAG nhận biết ngữ cảnh để hình thành cấu trúc bộ nhớ hai tầng, hiện thực năng lực phục vụ chủ động ở cấp cao hơn.

**Khái niệm cốt lõi**: bộ nhớ hai tầng, sự kiện có cấu trúc, truy xuất ngữ cảnh, phục vụ chủ động

### structured-knowledge-extraction - Trích xuất tri thức có cấu trúc
`chapter3/structured-knowledge-extraction/`

Lấy án lệ tư pháp làm ví dụ để chạy thông pipeline ba giai đoạn “phát hiện yếu tố từ dưới lên → phân cụm thành nguyên mẫu vụ án → Agent tư vấn đối thoại”: không đặt sẵn các trường cứng nhắc, để LLM tự phát hiện yếu tố từ lượng lớn án lệ và quy nạp thành schema mô-đun (yếu tố cốt lõi + yếu tố mở rộng theo tội danh); sau đó phân cụm vụ án thành nhiều nguyên mẫu và tính mức quan trọng của từng yếu tố trong mỗi nguyên mẫu; Agent sẽ khớp vụ việc mới với nguyên mẫu tương tự nhất, hỏi bổ sung thông tin còn thiếu theo mức quan trọng và đưa ra khuyến nghị có căn cứ (kèm tuyên bố miễn trừ trách nhiệm pháp lý).

**Khái niệm cốt lõi**: phát hiện tri thức từ dưới lên, yếu tố mô-đun, nguyên mẫu phân cụm, quyết định có thể giải thích

## 🛠️ Chương 4 · Công cụ

### perception-tools - MCP server cho công cụ cảm nhận
`chapter4/perception-tools/`

Xây dựng bộ công cụ cảm nhận toàn diện, cung cấp khả năng tìm kiếm web, hiểu đa phương thức, thao tác hệ thống tệp và truy cập nguồn dữ liệu công cộng. Phần lớn chức năng dựa trên API mở miễn phí (DuckDuckGo, Open-Meteo, Yahoo Finance, OpenStreetMap, v.v.) và không cần API key.

**Khái niệm cốt lõi**: giao thức MCP, phân tích đa phương thức, nguồn dữ liệu công cộng, hiểu tài liệu, dịch vụ thông tin địa lý

### execution-tools - MCP server cho công cụ thực thi
`chapter4/execution-tools/`

Triển khai bộ công cụ thực thi có cơ chế an toàn, bao gồm thao tác file, code interpreter, terminal ảo và tích hợp hệ thống bên ngoài. Dùng cơ chế phê duyệt lần hai bằng LLM để ngăn thao tác nguy hiểm, tự động tóm tắt đầu ra phức tạp và kiểm tra cú pháp mã.

**Khái niệm cốt lõi**: giao thức MCP, an toàn thực thi, phê duyệt bằng LLM, tóm tắt kết quả, xác minh tự động

### collaboration-tools - MCP server cho công cụ cộng tác
`chapter4/collaboration-tools/`

Cung cấp năng lực cộng tác toàn diện, gồm tự động hóa trình duyệt (framework browser-use), phối hợp người-máy (Human-in-the-Loop), thông báo đa kênh (Email, Telegram, Slack, Discord) và quản lý bộ hẹn giờ. Hỗ trợ phê duyệt quản trị viên cho thao tác nhạy cảm và lập lịch tác vụ định kỳ.

**Khái niệm cốt lõi**: giao thức MCP, tự động hóa trình duyệt, mô thức HITL, thông báo đa kênh, tác vụ định kỳ

### agent-with-event-trigger - Agent kích hoạt theo sự kiện và tích hợp MCP
`chapter4/agent-with-event-trigger/`

Agent hướng sự kiện hiện đại xây dựng trên FastAPI, mặc định tích hợp toàn bộ công cụ của ba MCP server phía trên. Dùng kiến trúc bất đồng bộ nguyên sinh để tải công cụ MCP rõ ràng; nhận sự kiện đa nguồn qua HTTP API (Web, tin nhắn tức thời, GitHub, timer, v.v.). Cung cấp tài liệu API tự động (Swagger UI) và khả năng giám sát nền.

**Khái niệm cốt lõi**: FastAPI, bất đồng bộ nguyên sinh, tích hợp MCP, hướng sự kiện, tài liệu API tự động, điều phối công cụ

### active-tool-selection - Chủ động chọn công cụ
`chapter4/active-tool-selection/`

Triển khai cơ chế chọn công cụ thông minh, giúp Agent chủ động chọn tổ hợp công cụ phù hợp nhất theo nhu cầu nhiệm vụ, thay vì thụ động tiếp nhận bộ công cụ định nghĩa sẵn.

**Khái niệm cốt lõi**: chọn công cụ, tải công cụ động, phân tích nhiệm vụ

### async-agent - Agent bất đồng bộ có khả năng thực thi song song và ngắt
`chapter4/async-agent/`

Triển khai lõi framework Agent bất đồng bộ hướng sự kiện (Flux) dựa trên asyncio một luồng: hàng đợi sự kiện inbox phân phối theo mức khẩn cấp (ngắt/ngay lập tức/xếp hàng), hỗ trợ công cụ bất đồng bộ chạy song song, ngắt turn hiện tại trong lúc đang chạy, đồng thời hủy và truy vấn trạng thái các tác vụ dài mô phỏng. Quyết định được thực hiện bởi LLM thật (function calling).

**Khái niệm cốt lõi**: lập trình bất đồng bộ, hàng đợi sự kiện, cơ chế ngắt, hủy công cụ song song, I/O không chặn

> Ngoài ra, `chapter4/docker-compose.yml` và `chapter4/DOCKER_DEPLOYMENT.md` cung cấp phương án tham khảo để container hóa và triển khai các MCP tool server nói trên.

## 💻 Chương 5 · Coding Agent và sinh mã

### coding-agent - Coding Agent cấp sản xuất
`chapter5/coding-agent/`

Trợ lý lập trình AI cấp sản xuất xây dựng trên Claude, triển khai toàn bộ công cụ bằng Python thuần, không phụ thuộc dòng lệnh. Bao gồm 17 công cụ hoàn chỉnh, bao phủ thao tác file, tìm kiếm, thao tác Shell và quản lý dự án. Đặc biệt triển khai công cụ Grep bằng Python thuần, tương thích đầy đủ với chức năng của ripgrep.

**Tính năng cốt lõi**:
- Triển khai bằng Python thuần, không phụ thuộc dòng lệnh, đặc biệt phù hợp với người dùng Mac
- Bộ công cụ đầy đủ: đọc/ghi/chỉnh sửa file, tìm kiếm regex bằng Python thuần, liệt kê thư mục, quản lý phiên Shell
- Kỹ thuật system prompt: timestamp, số lần gọi công cụ, quản lý TODO list, thông tin lỗi chi tiết
- Môi trường Shell bền vững, tự động phát hiện Lint, hỗ trợ phản hồi streaming
- Hỗ trợ nhiều nhà cung cấp LLM (Anthropic, OpenAI, OpenRouter)

**Khái niệm cốt lõi**: sinh mã, chỉnh sửa file, công cụ Python thuần, system prompt, kiểm tra Lint, hỗ trợ đa nhà cung cấp

### code-for-math - Dùng mã để nâng cao năng lực giải toán
`chapter5/code-for-math/`

Cho cùng một mô hình đối chiếu hai chế độ “chuỗi suy nghĩ thuần” và “có mã hỗ trợ” trên cùng một tập bài toán thi đấu: chế độ sau hình thức hóa đề thành Python (sympy/numpy/scipy), thực thi qua function calling trong sandbox tiến trình con, dùng tính toán chính xác thay cho tính nhẩm dễ sai, nhờ đó đạt độ chính xác cao hơn đáng kể.

**Khái niệm cốt lõi**: code interpreter, tính toán ký hiệu, so sánh chuỗi suy nghĩ, suy luận tăng cường bằng công cụ

### code-for-logic - Dùng mã để nâng cao năng lực suy nghĩ logic
`chapter5/code-for-logic/`

Chuyển các câu đố logic “hiệp sĩ và kẻ nói dối” thành bài toán thỏa mãn ràng buộc (CSP): Agent dùng `python-constraint` để định nghĩa biến và ràng buộc hai chiều rồi gọi solver, so sánh độ đúng của hai chế độ suy luận ngôn ngữ tự nhiên thuần và có mã hỗ trợ trên một tập câu đố K&K.

**Khái niệm cốt lõi**: giải ràng buộc, mô hình hóa CSP, suy luận hình thức, hỗ trợ bằng mã

### small-model-codified-rules - Quy tắc mã hóa cho mô hình nhỏ
`chapter5/small-model-codified-rules/`

Thí nghiệm đối chứng dựa trên ngữ cảnh chăm sóc khách hàng hàng không của τ-bench: sau khi chuyển chính sách nghiệp vụ phức tạp (quy tắc hoàn tiền) từ prompt ngôn ngữ tự nhiên vào mã/công cụ, tỷ lệ thành công nhiệm vụ và tính nhất quán chính sách của mô hình nhỏ tăng mạnh; kiểm tra bằng mã trong công cụ có thể chặn nhận thức sai của mô hình theo thời gian thực.

**Khái niệm cốt lõi**: quy tắc nghiệp vụ được mã hóa, thực thi chính sách, kiểm tra trong công cụ, độ tin cậy của mô hình nhỏ

### paper-to-ppt - Tự động tạo PPT từ bài báo (Proposer-Reviewer)
`chapter5/paper-to-ppt/`

Tái cấu trúc “làm PPT” thành bài toán sinh mã: Proposer viết mã Slidev (Markdown+HTML), Reviewer render từng trang thành PNG thật và dùng Vision LLM kiểm tra vấn đề dàn trang, rồi lặp sửa theo phản hồi có cấu trúc; phân công hai Agent giúp đỉnh ngữ cảnh nhỏ hơn đáng kể.

**Khái niệm cốt lõi**: sinh mã, Slidev, proposer-reviewer, kiểm soát chất lượng bằng thị giác

### paper-to-video - Tự động tạo video giảng giải bài báo
`chapter5/paper-to-video/`

Trên nền “bài báo → PPT”, sinh lời thuyết minh nói tự nhiên cho từng trang slide, gọi TTS để tổng hợp giọng nói, rồi dùng ffmpeg ghép ảnh chụp từng trang với âm thanh tương ứng thành một video thuyết minh có lồng tiếng.

**Khái niệm cốt lõi**: sinh đa phương tiện, sinh lời thuyết minh, TTS, đồng bộ âm thanh-hình ảnh bằng ffmpeg

### video-edit - Biên tập video thông minh dựa trên API
`chapter5/video-edit/`

Người dùng đưa một video nhiều cảnh + một yêu cầu ngôn ngữ tự nhiên; Agent dùng “định vị Vision hai bước” (trước lấy khung hình thô, sau tinh chỉnh đọc ảnh) để xác định ranh giới thời gian của cảnh mục tiêu, cắt đoạn rồi để Reviewer trích khung hình chính của thành phẩm để kiểm tra; nếu không đạt thì lặp lại.

**Khái niệm cốt lõi**: biên tập video, định vị bằng Vision, từ thô đến tinh, proposer-reviewer

### adaptive-log-parser - Hệ thống phân tích log tự thích ứng
`chapter5/adaptive-log-parser/`

Một hệ thống phân tích log có thể tự tiến hóa: khi gặp định dạng mới không phân tích được, hệ thống không báo lỗi dừng lại mà giao mẫu thất bại và lỗi cho Agent sinh mã để tạo hàm `parse`; sau khi tự động kiểm thử thành công, hàm được hot-update vào engine phân tích, toàn bộ quy trình không cần can thiệp thủ công.

**Khái niệm cốt lõi**: mã như bộ thích ứng hệ thống, vòng tự chữa lành, hot-update mã, kiểm thử tự động

### log-diagnosis - Hệ thống chẩn đoán log sản xuất thông minh
`chapter5/log-diagnosis/`

Agent chẩn đoán đọc log trajectory sản xuất, tài liệu kiến trúc và PRD, tự động định vị vấn đề và nguyên nhân gốc, sinh báo cáo có cấu trúc và test case hồi quy, dùng framework replay để thực thi xác minh thật, và (mock) kết nối GitHub qua MCP để tạo Issue.

**Khái niệm cốt lõi**: chẩn đoán trajectory, định vị nguyên nhân gốc, sinh test hồi quy, xác minh bằng replay

### dynamic-form - Hệ thống biểu mẫu động để làm rõ ý định
`chapter5/dynamic-form/`

Khi đối mặt với yêu cầu thiếu thông tin, Agent không hỏi từng câu một mà sinh động một biểu mẫu HTML tự chứa có logic liên kết để người dùng bổ sung một lần; frontend tổng hợp biểu mẫu thành JSON rồi trả lại Agent để tiếp tục nhiệm vụ.

**Khái niệm cốt lõi**: sinh mã, làm rõ ý định, biểu mẫu động, logic liên kết

### erp-agent - Agent ERP ngôn ngữ tự nhiên (NL → SQL)
`chapter5/erp-agent/`

Chuyển truy vấn tiếng Trung tự nhiên thành SQL để cơ sở dữ liệu thực thi và hiển thị trực tiếp bảng kết quả. Cốt lõi là mô thức artifact: LLM chỉ sinh artifact SQL, không tự vận chuyển dữ liệu; vừa tiết kiệm token vừa tránh sai do tính tay, ngay cả kết quả hàng chục nghìn dòng cũng trả về trong vài giây.

**Khái niệm cốt lõi**: NL2SQL, mô thức artifact, thực thi cơ sở dữ liệu, chi phí và độ chính xác

### conversational-ui - Hệ thống tùy biến giao diện bằng hội thoại
`chapter5/conversational-ui/`

Người dùng nêu yêu cầu tùy biến UI bằng ngôn ngữ tự nhiên (màu sắc/phông chữ/nội dung/bố cục), Agent tự định vị và sửa mã nguồn frontend React, nhờ hot loading (HMR) của Vite để thay đổi có hiệu lực tức thì, hỗ trợ tùy biến lặp nhiều vòng.

**Khái niệm cốt lõi**: sửa mã, tùy biến frontend, hot loading, lặp nhiều vòng

## 🎯 Chương 6 · Đánh giá Agent

### terminal-bench - Benchmark môi trường terminal
`chapter6/terminal-bench/`

Terminal-Bench là benchmark kiểm thử biểu hiện của AI Agent trong môi trường terminal thực. Từ biên dịch mã đến huấn luyện mô hình, thiết lập server, benchmark đánh giá cách Agent xử lý các nhiệm vụ đầu-cuối thực tế. Bao gồm bộ dữ liệu khoảng 100 nhiệm vụ và framework thực thi, hỗ trợ nhiều triển khai Agent.

**Khái niệm cốt lõi**: tự động hóa terminal, đánh giá nhiệm vụ, sandbox Docker, benchmark

### SWE-bench - Benchmark kỹ thuật phần mềm
`chapter6/SWE-bench/`

SWE-bench là benchmark đánh giá khả năng của mô hình ngôn ngữ lớn trong việc giải quyết các vấn đề GitHub thật. Với một codebase và mô tả issue, mô hình cần sinh patch có thể giải quyết vấn đề. Bao gồm nhiều phiên bản: SWE-bench, SWE-bench Lite, SWE-bench Verified và SWE-bench Multimodal.

**Khái niệm cốt lõi**: sửa mã, issue GitHub, sinh patch, đánh giá bằng Docker

### GAIA - Benchmark trợ lý AI tổng quát
`chapter6/GAIA/`

GAIA nhằm đánh giá thế hệ LLM tiếp theo (LLM có năng lực tăng cường bằng công cụ, prompt hiệu quả, truy cập tìm kiếm, v.v.). Bao gồm hơn 450 câu hỏi phi tầm thường cần mức độ công cụ và tự chủ khác nhau, với đáp án rõ ràng không mơ hồ. Chia thành 3 cấp độ khó.

**Khái niệm cốt lõi**: sử dụng công cụ, suy luận nhiều bước, đánh giá tính tự chủ

### OSWorld - Benchmark Agent cấp hệ điều hành
`chapter6/OSWorld/`

Đánh giá năng lực của Agent khi thực thi nhiệm vụ phức tạp trong môi trường hệ điều hành đầy đủ, bao gồm quản lý file, thao tác ứng dụng và cấu hình hệ thống.

**Khái niệm cốt lõi**: tự động hóa hệ điều hành, phối hợp nhiều ứng dụng, nhiệm vụ cấp hệ thống

### android_world - Benchmark môi trường Android
`chapter6/android_world/` (📖 kho bên ngoài, xem “Lấy kho bên ngoài”)

Đánh giá biểu hiện của Agent trong môi trường di động Android, bao gồm điều hướng ứng dụng, tương tác UI và khả năng hoàn thành nhiệm vụ.

**Khái niệm cốt lõi**: tự động hóa di động, Android UI, tương tác ứng dụng

> `chapter6/android-world/` (tên có dấu gạch nối) không phải mã benchmark, mà là ghi chú phân tích của sách về các ca thất bại của T3A Agent trên android_world (`t3a*.md`), có thể dùng làm tài liệu đọc tham khảo.

### tau2-bench - Benchmark suy luận tăng cường bằng công cụ
`chapter6/tau2-bench/`

Tập trung đánh giá năng lực Agent dùng công cụ để suy luận phức tạp, bao gồm tính toán, tìm kiếm, xử lý dữ liệu và các ngữ cảnh khác.

**Khái niệm cốt lõi**: suy luận tăng cường bằng công cụ, nhiệm vụ nhiều bước, tổ hợp công cụ

### elo-leaderboard - Hệ thống bảng xếp hạng ELO
`chapter6/elo-leaderboard/`

Triển khai bảng xếp hạng hiệu năng Agent dựa trên hệ thống điểm ELO, đánh giá năng lực tương đối của các Agent khác nhau thông qua so sánh đối đầu.

**Khái niệm cốt lõi**: điểm ELO, đánh giá tương đối, hệ thống bảng xếp hạng

### model-benchmark - Benchmark hiệu năng mô hình đa chiều
`chapter6/model-benchmark/`

Benchmark ngang nhiều nhà cung cấp LLM API tương thích OpenAI; dùng giao diện streaming để đo chính xác độ trễ token đầu tiên (TTFT), đo các phân vị độ trễ đầu-cuối (p50/p95), throughput và tỷ lệ thành công dưới tải đồng thời. Một lệnh tạo bảng so sánh đa chiều, cho thấy chọn mô hình là đánh đổi nhiều chiều chứ không chỉ nhìn bảng xếp hạng.

**Khái niệm cốt lõi**: TTFT, phân vị độ trễ, throughput, stress test đồng thời, chọn mô hình

### agent-cost-analysis - Phân tích chi phí đầu-cuối cho nhiệm vụ Agent
`chapter6/agent-cost-analysis/`

Phân rã toàn tuyến chi phí của nhiệm vụ Agent nhiều vòng điển hình (hoàn tiền chăm sóc khách hàng): dùng tracing nhẹ tự xây để ghi lại token input/output/cache, độ trễ và chi phí của từng lần gọi LLM; tổng hợp “bước nào đắt nhất”, rồi dùng A/B để định lượng mức tiết kiệm thực của thiết kế thân thiện KV-cache + nén ngữ cảnh.

**Khái niệm cốt lõi**: observability, phân rã chi phí, prompt caching, so sánh A/B

### tts-quality-eval - Pipeline đánh giá chất lượng TTS hoàn toàn tự động
`chapter6/tts-quality-eval/`

Dùng nhiều cấu hình TTS (model/voice/speed khác nhau) để tổng hợp cùng một nhóm văn bản thử thách, sau đó dùng LLM-as-a-Judge đa phương thức chấm điểm từng chiều theo Rubric (độ rõ/naturalness, v.v.), tổng hợp thành bảng so sánh cấu hình có thể tái hiện.

**Khái niệm cốt lõi**: LLM-as-a-Judge, chấm điểm Rubric, đánh giá TTS, so sánh đa chiều

## 🧠 Chương 7 · Hậu huấn luyện mô hình

Chương này bao gồm nhiều dự án hậu huấn luyện mô hình, bao phủ fine-tuning có giám sát (SFT), học tăng cường (RL) cùng nhiều kỹ thuật và ngữ cảnh ứng dụng.

### AdaptThink - Độ sâu suy luận thích ứng
`chapter7/AdaptThink/` và `chapter7/AdaptThink-original/`

Cho mô hình suy luận học cách chọn chế độ suy luận thích ứng theo độ khó của câu hỏi (Thinking vs NoThinking). Thông qua tối ưu có ràng buộc và importance sampling, dự án giảm mạnh chi phí suy luận (45–69%) đồng thời nâng cao độ chính xác. Dựa trên mô hình DeepSeek-R1-Distill-Qwen, huấn luyện bằng thuật toán DAPO.

**Khái niệm cốt lõi**: suy luận thích ứng, tối ưu chi phí suy luận, tối ưu có ràng buộc, importance sampling

### retool - Suy luận toán học tăng cường bằng công cụ
`chapter7/retool/`

Dùng hội thoại nhiều vòng và sandbox mã để nâng cao năng lực suy luận toán học của mô hình ngôn ngữ lớn. Thông qua hai giai đoạn SFT và RL, mô hình học cách dùng môi trường thực thi mã để hỗ trợ giải bài toán. Dựa trên Qwen2.5-32B-Instruct, huấn luyện trên bộ AIME 2024, dùng thuật toán DAPO và sandbox SandboxFusion.

**Khái niệm cốt lõi**: sử dụng công cụ, thực thi mã, suy luận toán học, hội thoại nhiều vòng, thuật toán DAPO

### AWorld / AWorld-train - Huấn luyện Agent hiện thân
`chapter7/AWorld/` và `chapter7/AWorld-train/`

Huấn luyện Agent hiện thân dựa trên framework AWorld, giúp Agent thực thi nhiệm vụ phức tạp trong môi trường ảo và học từ kinh nghiệm.

**Khái niệm cốt lõi**: trí tuệ hiện thân, tương tác môi trường, học từ kinh nghiệm

### SFTvsRL - Nghiên cứu so sánh SFT và RL
`chapter7/SFTvsRL/`

So sánh có hệ thống hiệu quả của fine-tuning có giám sát (SFT) và học tăng cường (RL) trên các nhiệm vụ khác nhau, phân tích ưu nhược điểm và ngữ cảnh phù hợp của hai phương pháp.

**Khái niệm cốt lõi**: SFT vs RL, so sánh phương pháp huấn luyện, phân tích hiệu năng

### verl - Framework huấn luyện RL hiệu quả
`chapter7/verl/`

verl là framework học tăng cường hiệu quả được thiết kế riêng cho huấn luyện RLHF của mô hình ngôn ngữ lớn, hỗ trợ nhiều thuật toán như PPO, GRPO, DAPO.

**Khái niệm cốt lõi**: RLHF, PPO, huấn luyện phân tán, tối ưu hiệu quả

### Intuitor - Huấn luyện suy luận trực giác
`chapter7/Intuitor/`

Huấn luyện năng lực suy luận trực giác của mô hình, giúp mô hình có thể nhanh chóng đưa ra phán đoán hợp lý mà không cần chuỗi suy nghĩ chi tiết.

**Khái niệm cốt lõi**: suy luận trực giác, ra quyết định nhanh, tối ưu chuỗi suy nghĩ

### MultilingualReasoning - Suy luận đa ngôn ngữ
`chapter7/MultilingualReasoning/`

Huấn luyện năng lực suy luận của mô hình trong môi trường nhiều ngôn ngữ, nâng cao biểu hiện trên các nhiệm vụ xuyên ngôn ngữ.

**Khái niệm cốt lõi**: đa ngôn ngữ, suy luận xuyên ngôn ngữ, khái quát hóa ngôn ngữ

### SpatialReasoning - Huấn luyện suy luận không gian
`chapter7/SpatialReasoning/`

Tập trung huấn luyện năng lực suy luận không gian của mô hình, xử lý các vấn đề liên quan đến vị trí, phương hướng, khoảng cách và các quan hệ không gian khác.

**Khái niệm cốt lõi**: suy luận không gian, hiểu hình học, quan hệ vị trí

### SimpleVLA-RL - RL thị giác-ngôn ngữ-hành động
`chapter7/SimpleVLA-RL/`

Huấn luyện học tăng cường kết hợp thị giác, ngôn ngữ và hành động, giúp mô hình hiểu đầu vào thị giác và thực hiện hành động tương ứng.

**Khái niệm cốt lõi**: thị giác-ngôn ngữ-hành động, RL đa phương thức, trí tuệ hiện thân

### continued-pretraining - Tiền huấn luyện tiếp tục
`chapter7/continued-pretraining/`

Tiếp tục tiền huấn luyện trên dữ liệu miền cụ thể để nâng cao biểu hiện của mô hình trong miền mục tiêu.

**Khái niệm cốt lõi**: tiền huấn luyện tiếp tục, thích ứng miền, nạp tri thức

### MiniMind-pretrain - Tiền huấn luyện mô hình nhỏ
`chapter7/MiniMind-pretrain/`

Tiền huấn luyện mô hình ngôn ngữ nhỏ từ con số 0, hiểu toàn bộ quy trình và kỹ thuật then chốt của tiền huấn luyện.

**Khái niệm cốt lõi**: tiền huấn luyện, mô hình nhỏ, quy trình huấn luyện

### sesame - Mô hình hóa và đánh giá chuỗi
`chapter7/sesame/`

Tập trung vào phương pháp huấn luyện và đánh giá cho nhiệm vụ mô hình hóa chuỗi.

**Khái niệm cốt lõi**: mô hình hóa chuỗi, phương pháp đánh giá, tối ưu hiệu năng

### orpheus - Sinh và hiểu âm nhạc
`chapter7/orpheus/`

Huấn luyện năng lực sinh và hiểu âm nhạc của mô hình.

**Khái niệm cốt lõi**: sinh âm nhạc, hiểu âm thanh, AI sáng tạo

### tinker-cookbook - Tuyển tập kỹ thuật huấn luyện
`chapter7/tinker-cookbook/`

Tập hợp nhiều kỹ thuật thực dụng và best practice cho huấn luyện mô hình.

**Khái niệm cốt lõi**: kỹ thuật huấn luyện, best practice, phương pháp tuning

## 🔄 Chương 8 · Tự tiến hóa của Agent

Chương này tập trung vào cách giúp Agent liên tục trưởng thành từ kinh nghiệm mà không cần thay đổi trọng số: lắng đọng trajectory thành công thành kinh nghiệm tái sử dụng được, ngoại hóa thao tác lặp lại thành công cụ, và chưng cất prompt cùng quan sát vào mô hình.

### gaia-experience - Học từ kinh nghiệm thành công
`chapter8/gaia-experience/`

Dựa trên framework AWorld và benchmark GAIA, triển khai vòng kín “học - áp dụng” hoàn chỉnh. Agent tự động tóm tắt trajectory nhiệm vụ thành công thành kinh nghiệm có cấu trúc, sau đó truy xuất và áp dụng trong nhiệm vụ mới để hiện thực tự tiến hóa.

**Khái niệm cốt lõi**: học từ kinh nghiệm, tóm tắt chiến lược, tóm tắt trajectory, tự tiến hóa

### browser-use-rpa - Ghi và phát lại workflow
`chapter8/browser-use-rpa/`

Triển khai hệ thống ghi workflow cho tự động hóa trình duyệt, tự động đóng gói chuỗi thao tác lặp lại thành công cụ tham số hóa. Bằng cách chuyển từ suy luận LLM đắt đỏ sang thực thi tự động hóa chính xác, tốc độ tăng 3–5 lần.

**Khái niệm cốt lõi**: ghi workflow, RPA, sinh công cụ, học được ngoại hóa

### prompt-distillation - Chưng cất prompt
`chapter8/prompt-distillation/`

Chưng cất hiệu quả của prompt phức tạp vào tham số mô hình, giảm độ dài prompt khi suy luận và cố định kinh nghiệm trong ngữ cảnh thành tri thức tham số hóa.

**Khái niệm cốt lõi**: chưng cất tri thức, tối ưu prompt, tri thức tham số hóa

### prompt-auto-optimization - Tự động tối ưu system prompt
`chapter8/prompt-auto-optimization/`

Học system prompt tự động dựa trên phản hồi con người: lấy vấn đề “chuyển tiếp quá mức” trong chăm sóc khách hàng hàng không kiểu tau-bench làm ví dụ, cho một Coding Agent đọc file system prompt, định vị quy tắc có vấn đề, sinh chỉnh sửa chính xác và thật sự viết lại file prompt, sau đó đánh giá lại để xác minh, tạo thành vòng kín “phản hồi → viết lại → xác minh”.

**Khái niệm cốt lõi**: tự động tối ưu prompt, phản hồi con người, Coding Agent, đánh giá vòng kín

### active-tool-discovery - Chủ động phát hiện công cụ
`chapter8/active-tool-discovery/`

So sánh hai mô thức “nhồi toàn bộ hơn 120 tool schema” và “chủ động phát hiện theo nhu cầu”: mô thức sau chỉ giữ một số ít công cụ nền tảng + một meta-tool `discover_tools` trong system, dùng độ tương tự embedding để truy xuất 3–5 công cụ chuyên dụng liên quan nhất từ thư viện công cụ, vừa tiết kiệm token vừa tránh mô hình chọn sai/lạm dụng công cụ chung khi danh sách công cụ quá dài.

**Khái niệm cốt lõi**: chủ động phát hiện công cụ, truy xuất embedding, tối ưu token, tuân thủ chỉ dẫn

### self-evolving-tools - Tự tiến hóa bằng cách tìm công cụ trên web
`chapter8/self-evolving-tools/`

Phong cách Alita “định nghĩa sẵn tối thiểu, tự tiến hóa tối đa”: Agent không cài sẵn công cụ miền nào, chỉ có năm meta-tool tổng quát; khi gặp nhiệm vụ chưa biết làm, nó tự lên mạng tìm thư viện/API mã nguồn mở, đọc tài liệu, kiểm thử trong sandbox, đóng gói phương án khả thi thành công cụ mới đưa vào thư viện công cụ và tái sử dụng, toàn quy trình nhấn mạnh kiểm soát hallucination.

**Khái niệm cốt lõi**: tự tiến hóa, tạo công cụ, tái sử dụng công cụ, kiểm soát hallucination

### self-evolution-eval - Bộ dữ liệu đánh giá Agent tự tiến hóa
`chapter8/self-evolution-eval/`

Bộ dữ liệu chuyên dụng và phương pháp xác minh được thiết kế để đánh giá năng lực “tự tiến hóa” của Agent (tự phát hiện, tạo và tái sử dụng công cụ): 20 nhiệm vụ xuyên miền (không ám chỉ tên công cụ) + harness xác minh phân tầng bốn lớp + Agent tham chiếu có kiểm soát, vượt ra ngoài việc “kết quả đúng hay sai” để khảo sát chất lượng phát hiện, tạo và tái sử dụng.

**Khái niệm cốt lõi**: thiết kế bộ dữ liệu đánh giá, xác minh phân tầng, đo lường tái sử dụng công cụ, tự tiến hóa

## 🎙️ Chương 9 · Đa phương thức và tương tác thời gian thực

### live-audio - Đối thoại giọng nói thời gian thực
`chapter9/live-audio/`

Demo chat giọng nói thời gian thực, tích hợp speech-to-text, hội thoại AI và text-to-speech. Hỗ trợ nhiều nhà cung cấp dịch vụ AI (OpenAI, OpenRouter, ARK, Siliconflow), cung cấp trải nghiệm hội thoại độ trễ thấp.

**Tính năng cốt lõi**:
- Đầu vào giọng nói thời gian thực và VAD (Voice Activity Detection)
- Hỗ trợ đa nhà cung cấp: ASR (OpenAI Whisper, SenseVoice), LLM (GPT-4o, Gemini, Doubao), TTS (Fish Audio)
- Giao tiếp WebSocket thời gian thực, luồng âm thanh độ trễ thấp
- Giám sát độ trễ và ghi log thời gian thực

**Khái niệm cốt lõi**: nhận dạng giọng nói, hội thoại thời gian thực, TTS, WebSocket, kiến trúc đa nhà cung cấp

### browser-use - Agent tự động hóa trình duyệt (Computer Use)
`chapter9/browser-use/`

Browser-Use là framework tự động hóa trình duyệt mạnh mẽ, cho phép LLM điều khiển trình duyệt để hoàn thành nhiệm vụ phức tạp. Hỗ trợ điền form, điều hướng trang web, trích xuất dữ liệu và nhiều ngữ cảnh khác; đây là một triển khai điển hình của tự động hóa GUI (Computer Use).

**Tính năng cốt lõi**:
- Tự động hóa trình duyệt do LLM điều khiển
- Hỗ trợ nhiều LLM (ChatBrowserUse, OpenAI, Google, mô hình cục bộ)
- Mở rộng công cụ tùy chỉnh, xử lý xác thực
- Hỗ trợ triển khai sandbox, tích hợp dịch vụ đám mây

**Khái niệm cốt lõi**: tự động hóa trình duyệt, Computer Use, hiểu thị giác, mở rộng công cụ

### claude-quickstarts - Khởi đầu nhanh với Claude
`chapter9/claude-quickstarts/`

Ví dụ khởi đầu nhanh và best practice cho Claude API, bao phủ nhiều ngữ cảnh sử dụng.

**Khái niệm cốt lõi**: Claude API, prompt engineering, best practice

### phone-agent - Agent gọi điện thoại
`chapter9/phone-agent/`

Minh họa Agent giọng nói “thay người dùng gọi điện tương tác với thế giới bên ngoài”: tầng trên là ReAct Agent tiêu chuẩn; sau khi nhận nhiệm vụ ngôn ngữ tự nhiên, nó tự xác định số điện thoại và mục tiêu cuộc gọi, gọi công cụ `make_phone_call` (dựa trên trừu tượng API giọng nói điện thoại) để hoàn tất toàn bộ cuộc gọi, đọc bản ghi cuộc gọi có cấu trúc, hỏi lại và gọi tiếp khi cần, cuối cùng báo cáo cho người dùng.

**Khái niệm cốt lõi**: Agent giọng nói, tương tác điện thoại, ReAct, trừu tượng công cụ

### end-to-end-speech - Suy nghĩ bằng giọng nói đầu-cuối vs pipeline nối tầng
`chapter9/end-to-end-speech/`

Tương ứng với mô thức suy nghĩ bằng giọng nói đầu-cuối của Step-Audio R1 (một mô hình duy nhất “nghe → nghĩ → nói”): chạy thông vòng kín “đầu vào giọng nói → suy nghĩ → đầu ra giọng nói”, đồng thời so sánh trực quan với mô thức nối tầng ASR→LLM→TTS về độ trễ và mất mát thông tin cận ngôn ngữ (cảm xúc/ngữ điệu/tốc độ nói).

**Khái niệm cốt lõi**: giọng nói đầu-cuối, so sánh nối tầng, thông tin cận ngôn ngữ, vừa nghĩ vừa nói

### streaming-speech - Mô phỏng cảm nhận giọng nói streaming
`chapter9/streaming-speech/`

Minh họa đánh đổi cốt lõi của cảm nhận giọng nói streaming: chia âm thanh liên tục thành các khối có độ dài tăng dần đưa vào ASR; mỗi khi nhận một đoạn nhỏ thì xuất “kết quả nhận dạng phần hiện tại” để có văn bản cực sớm với độ trễ gói đầu rất thấp. Cái giá là các khối ban đầu có thể sai do thiếu ngữ cảnh nửa sau câu; khi âm thanh tích lũy, kết quả dần hội tụ, đối chiếu với cách “đợi đủ cả câu rồi nhận dạng” có độ chính xác cao nhưng độ trễ cao.

**Khái niệm cốt lõi**: cảm nhận streaming, nhận dạng theo khối, độ trễ gói đầu, chi phí của quyết định quá sớm

### controllable-tts - TTS điều khiển bằng control tag
`chapter9/controllable-tts/`

Cho đầu ra của LLM chính mang theo control tag (cảm xúc/tốc độ/phong cách/ngắt nghỉ/tiếng cười); tầng thực thi phân tích tag và ánh xạ sang profile phong cách tương ứng trong thư viện giọng tham chiếu rồi tổng hợp giọng nói. Quyết định “ngắt ở đâu, dùng giọng điệu nào” được giao cho LLM; cùng một đoạn văn bản có thể được tổng hợp thành nhiều phong cách và cảm xúc khác nhau.

**Khái niệm cốt lõi**: TTS có thể điều khiển, control tag, thư viện giọng tham chiếu, điều khiển ngữ điệu

## 🤝 Chương 10 · Cộng tác đa Agent

### use-computer-while-calling - Kiến trúc hai Agent
`chapter10/use-computer-while-calling/` (📖 mã đầy đủ đã tách thành [19PINE-AI/TalkAct](https://github.com/19PINE-AI/TalkAct), thư mục này chỉ giữ tài liệu mô tả)

Triển khai kiến trúc cộng tác hai Agent gồm Agent gọi điện thoại và Agent sử dụng máy tính. Hai Agent giao tiếp trực tiếp qua WebSocket, không cần coordinator. Agent điện thoại xử lý tương tác giọng nói, Agent máy tính thực thi tự động hóa trình duyệt; hai bên làm việc song song để hoàn thành nhiệm vụ phức tạp cần cả giọng nói và thao tác web.

**Tính năng cốt lõi**:
- Giao tiếp trực tiếp giữa các Agent (không coordinator)
- Truyền thông điệp bằng gọi công cụ tiêu chuẩn
- Thao tác song song: hội thoại giọng nói + tự động hóa trình duyệt
- Giao thức thông điệp JSON đơn giản

**Thành phần kiến trúc**:
- Phone Call Agent (Node.js): I/O giọng nói, ASR/TTS, hội thoại LLM
- Computer Use Agent (Python): tự động hóa trình duyệt, browser-use, crawl trang web
- Giao tiếp WebSocket: truyền thông điệp trực tiếp giữa các Agent

**Khái niệm cốt lõi**: cộng tác đa Agent, giao tiếp giữa Agent, xử lý nhiệm vụ song song, tích hợp giọng nói + trình duyệt

### staged-system-prompt - Chuyển system prompt theo giai đoạn thực thi
`chapter10/staged-system-prompt/`

Cùng một Coding Agent tải system prompt và bộ công cụ khác nhau ở các giai đoạn thực thi khác nhau của nhiệm vụ (làm rõ yêu cầu → triển khai mã → review mã), nhờ đó trong một cuộc hội thoại có thể đóng các vai khác nhau và biểu hiện hành vi khác nhau; lịch sử hội thoại và trạng thái nhiệm vụ được chia sẻ liên tục giữa các giai đoạn, nếu review không đạt còn có thể quay lại giai đoạn triển khai.

**Khái niệm cốt lõi**: prompt theo giai đoạn, chuyển vai trò, ngữ cảnh chia sẻ, pipeline theo giai đoạn

### multi-role-transfer - Chuyển đổi nhiều vai trò và tự chủ bàn giao
`chapter10/multi-role-transfer/`

Minh họa handoff dạng chuỗi trong ngữ cảnh chia sẻ: trong một phiên có nhiều Agent vai trò chuyên môn, mỗi Agent có system prompt và bộ công cụ chuyên biệt riêng; thông qua công cụ `transfer_to_agent`, Agent tự chủ phán đoán nên chuyển sang vai trò nào theo tiến triển nhiệm vụ. Vì cùng chia sẻ một lịch sử hội thoại, ngữ cảnh đầy đủ được giữ tự nhiên khi bàn giao.

**Khái niệm cốt lõi**: bàn giao vai trò, handoff, ngữ cảnh chia sẻ, chuyển đổi tự chủ

### book-translation - Agent dịch sách (mô thức quản lý)
`chapter10/book-translation/`

Dùng mô thức quản lý (Orchestration) để chia bản dịch tài liệu dài cho các Agent chuyên trách như thuật ngữ/biên dịch/hiệu đính: Manager chỉ lưu nhiệm vụ, kế hoạch, bản ghi gọi và chỉ mục file; toàn bộ bản dịch được ghi ra đĩa, nên ngữ cảnh gần như ổn định. Đồng thời so sánh với phương án đơn Agent, dùng số token thật để giải thích cách kiểm soát phình ngữ cảnh và dùng bảng thuật ngữ chia sẻ để đảm bảo tính nhất quán toàn sách.

**Khái niệm cốt lõi**: mô thức quản lý, cách ly ngữ cảnh, kiểm soát phình ngữ cảnh, bảng thuật ngữ chia sẻ

### parallel-web-research - Agent thu thập thông tin đa nguồn song song
`chapter10/parallel-web-research/`

Minh họa nhiều Agent đồng cấu tìm kiếm song song + điều phối trung tâm: coordinator chính đồng thời khởi động N sub-Agent, mỗi sub-Agent truy cập một nguồn để tìm câu trả lời; khi một bên tìm trúng mục tiêu, các bên còn lại dừng nhẹ nhàng ngay. Message bus, phân phối song song, giám sát thời gian thực, kết thúc dây chuyền và xử lý race condition đều được triển khai thật (dùng nguồn thông tin mô phỏng có kiểm soát thay cho trình duyệt thật).

**Khái niệm cốt lõi**: Agent song song, điều phối trung tâm, message bus, kết thúc dây chuyền

### voice-werewolf - Hệ thống Agent Ma sói bằng giọng nói
`chapter10/voice-werewolf/`

Dùng trò chơi Ma sói đa Agent để minh họa kiểm soát quyền thông tin khi “không chia sẻ ngữ cảnh”: mỗi người chơi là một LLM Agent độc lập và duy trì ngữ cảnh riêng được cách ly nghiêm ngặt; trọng tài xác định do mã điều khiển sẽ quyết định mỗi thông tin được gửi vào ngữ cảnh của người chơi nào và ghi audit, sau khi game kết thúc tự động kiểm tra cách ly có đúng không. Giọng nói là phần tăng cường tùy chọn.

**Khái niệm cốt lõi**: bất đối xứng thông tin, cách ly ngữ cảnh riêng, điều phối trọng tài, xác minh audit

## 📖 Gợi ý học tập

### Tư tưởng cốt lõi: Agent = mô hình + context + tools

Khung cốt lõi của sách là **Agent = mô hình + context + tools**. Ba thành phần này phối hợp với nhau để hiện thực hành vi thông minh của Agent:

- **Mô hình (Model)**: bộ não của Agent, cung cấp năng lực hiểu, suy luận và ra quyết định
- **Ngữ cảnh (Context)**: hệ điều hành của Agent, bao gồm chỉ dẫn hệ thống, lịch sử hội thoại, quá trình suy luận, bản ghi tương tác công cụ, v.v.
- **Công cụ (Tools)**: đôi tay của Agent, giúp Agent cảm nhận môi trường, thực thi thao tác và tương tác với thế giới bên ngoài

### Lộ trình học

Lộ trình học tương ứng một-một với các chương của sách, triển khai từng lớp quanh ba trụ cột lớn:

- **Chương 1 · Phần nền tảng**: xây dựng khung nhận thức hoàn chỉnh về hệ thống Agent — hiểu định nghĩa Agent trong RL, so sánh khác biệt về hiệu quả mẫu giữa RL truyền thống và mô thức LLM+RL, hiểu mô hình mới “model as Agent”, nắm vững khung cốt lõi **Agent = mô hình + context + tools**. **Insight then chốt**: tầm quan trọng của tri thức tiên nghiệm vượt qua thuật toán và môi trường.

- **Chương 2–3 · Phần ngữ cảnh**: ngữ cảnh là hệ điều hành của Agent. Chương 2 bao phủ system prompt, thiết kế thân thiện KV Cache, nén ngữ cảnh và ablation prompt engineering; chương 3 bao phủ bộ nhớ người dùng, truy xuất dày đặc/thưa/lai, Agentic RAG, truy xuất nhận biết ngữ cảnh và trích xuất tri thức có cấu trúc. **Insight then chốt**: ngữ cảnh hoàn chỉnh bao gồm chỉ dẫn hệ thống, lịch sử hội thoại, quá trình suy luận, bản ghi tương tác công cụ, bộ nhớ người dùng và tri thức bên ngoài.

- **Chương 4–5 · Phần công cụ**: công cụ là cây cầu để Agent tương tác với thế giới. Chương 4 bao phủ ba loại công cụ MCP cảm nhận/thực thi/cộng tác, kích hoạt sự kiện và kiến trúc bất đồng bộ; chương 5 đi sâu vào triển khai đầy đủ Coding Agent cấp sản xuất. **Insight then chốt**: thiết kế công cụ nên tổng quát hóa (code interpreter tốt hơn calculator); mã là siêu năng lực có thể tạo ra công cụ mới.

- **Chương 6–7 · Phần mô hình**: cách đo lường và phóng đại trí tuệ. Chương 6 bao phủ các benchmark đánh giá như Terminal-Bench, SWE-bench, GAIA, OSWorld, Tau2-Bench; chương 7 bao phủ các kỹ thuật hậu huấn luyện như SFT, RL, RLHF và hiệu quả mẫu. **Insight then chốt**: tín hiệu xác minh độc lập đáng tin cậy hơn “để mô hình nghĩ lại một lần”; “model as Agent” dùng RL để nội hóa gọi công cụ thành năng lực nguyên sinh.

- **Chương 8 · Phần tự tiến hóa**: giúp Agent trưởng thành từ kinh nghiệm mà không cần đổi trọng số — học từ kinh nghiệm, ngoại hóa workflow thành công cụ, chưng cất prompt và quan sát vào tham số. **Insight then chốt**: học từ kinh nghiệm là chìa khóa để Agent đi từ “thông minh” tới “thành thạo”.

- **Chương 9–10 · Phần mở rộng và cộng tác**: chương 9 mở rộng cảm nhận và hành động từ văn bản sang giọng nói, GUI và thế giới vật lý; chương 10 xử lý nhiệm vụ phức tạp thông qua phân công cộng tác đa Agent. **Insight then chốt**: mọi quyết định thiết kế trong hệ thống đa Agent đều có thể tìm thấy đối ứng trong ba yếu tố của đơn Agent.

### Phân cấp độ khó

- **Nhập môn** (Chương 1–2): phù hợp với người mới bắt đầu, hiểu khái niệm cơ bản
- **Nâng cao** (Chương 3–4): cần nền tảng lập trình nhất định, liên quan đến tích hợp hệ thống
- **Cao cấp** (Chương 5–6): cần năng lực lập trình mạnh hơn, liên quan đến thiết kế hệ thống phức tạp
- **Chuyên gia** (Chương 7–8): cần kinh nghiệm học sâu và huấn luyện/tự tiến hóa
- **Ứng dụng** (Chương 9–10): tổng hợp kiến thức đã học để xây dựng ứng dụng thực tế

### Gợi ý thực hành

1. **Tự tay thực hành**: mỗi dự án đều được thiết kế để có thể chạy độc lập; khuyến nghị tự chạy và sửa mã
2. **Kết hợp với sách**: đọc cùng các chương tương ứng trong bản thảo tại [`book/`](book/) để hiểu sự kết hợp giữa lý thuyết và thực hành
3. **So sánh thí nghiệm**: nhiều dự án chứa nghiên cứu ablation và thí nghiệm đối chứng; hãy dùng so sánh để hiểu sâu hơn
4. **Học tăng dần**: bắt đầu từ dự án đơn giản rồi dần đi sâu vào hệ thống phức tạp
5. **Chú ý giao thức**: các dự án MCP server ở chương 4 minh họa giao thức công cụ chuẩn hóa, đây là chìa khóa để xây dựng Agent có thể mở rộng

## 🔑 API key

Khuyến nghị mọi người đăng ký API key của một vài nền tảng để tiện học:
- **Kimi**: https://platform.moonshot.cn/ Dòng Kimi của Moonshot AI, mạnh về ngữ cảnh dài và năng lực Agent
- **Zhipu GLM**: https://open.bigmodel.cn/ Dòng GLM của Zhipu AI (GLM-4.6, v.v.), năng lực tiếng Trung mạnh, hiệu quả chi phí cao, cũng rất được khuyến nghị
- **Siliconflow**: https://siliconflow.cn/ Có nhiều mô hình mã nguồn mở, bao gồm DeepSeek, Qwen, v.v.
- **Volcengine**: https://www.volcengine.com/product/ark Có các mô hình đóng của ByteDance (Doubao), độ trễ truy cập trong Trung Quốc tương đối thấp
- **OpenRouter**: https://openrouter.ai/ Có thể truy cập trực tiếp từ Trung Quốc tới nhiều mô hình đóng và mở ở nước ngoài, bao gồm Gemini 2.5 Pro, Claude 4 Sonnet, OpenAI GPT-5, v.v. (API chính thức cần IP và phương thức thanh toán ở nước ngoài; OpenAI còn cần xác minh danh tính ở nước ngoài, đăng ký khá phiền)

Có thể tham khảo chọn mô hình tại: https://01.me/2025/07/llm-api-setup/

## 📦 Phụ lục · Lấy kho bên ngoài

Vì lý do dung lượng và bản quyền, các benchmark đánh giá và framework huấn luyện dùng trong chương 6, 7 và 9 **không được tích hợp sẵn** trong kho này; bạn cần tự clone vào thư mục tương ứng (bên dưới là địa chỉ upstream và commit đã được sách kiểm chứng). Có thể lưu các lệnh sau thành script để kéo một lần:

```bash
# Chương 6 · Benchmark đánh giá
git clone https://github.com/google-research/android_world.git         chapter6/android_world
git clone https://huggingface.co/datasets/gaia-benchmark/GAIA          chapter6/GAIA
git clone https://github.com/xlang-ai/OSWorld.git                      chapter6/OSWorld
git clone https://github.com/SWE-bench/SWE-bench.git                   chapter6/SWE-bench
git clone https://github.com/sierra-research/tau2-bench.git            chapter6/tau2-bench
git clone https://github.com/laude-institute/terminal-bench.git        chapter6/terminal-bench

# Chương 7 · Framework huấn luyện (bojieli/* là nhánh được sách điều chỉnh)
git clone https://github.com/bojieli/minimind.git                      chapter7/MiniMind-pretrain/minimind      # Thí nghiệm 7-3 huấn luyện LLM từ đầu
git clone https://github.com/bojieli/minimind-v.git                    chapter7/MiniMind-pretrain/minimind-v    # Thí nghiệm 7-4 huấn luyện VLM từ đầu (projection layer)
git clone https://github.com/bojieli/AdaptThink.git                    chapter7/AdaptThink-original
git clone https://github.com/bojieli/AWorld.git                        chapter7/AWorld
git clone https://github.com/bojieli/SFTvsRL.git                       chapter7/SFTvsRL
git clone https://github.com/bojieli/verl.git                          chapter7/verl
git clone https://github.com/thinking-machines-lab/tinker-cookbook.git chapter7/tinker-cookbook
git clone https://github.com/bojieli/lighteval.git                     chapter7/Intuitor/lighteval
git clone https://github.com/19PINE-AI/rlvp.git                        chapter7/RLVP/rlvp                       # Thí nghiệm 7-14 mã bài báo RLVP
git clone https://github.com/PRIME-RL/SimpleVLA-RL.git                 chapter7/SimpleVLA-RL/SimpleVLA-RL       # Thí nghiệm 7-13 RL thị giác-ngôn ngữ-hành động

# Chương 9 · Tự động hóa trình duyệt và ví dụ Claude
git clone https://github.com/browser-use/browser-use.git               chapter9/browser-use
git clone https://github.com/anthropics/claude-quickstarts.git         chapter9/claude-quickstarts

# Chương 10 · Kiến trúc hai Agent (đã độc lập thành dự án TalkAct) + AI town của Stanford
git clone https://github.com/19PINE-AI/TalkAct.git                     chapter10/use-computer-while-calling
git clone https://github.com/joonspk-research/generative_agents.git    chapter10/generative_agents             # Thí nghiệm 10-7 AI town của Stanford
```

> Nếu README của từng dự án ghi rõ commit cụ thể, hãy `git checkout` tới phiên bản tương ứng theo hướng dẫn để đảm bảo kết quả tái hiện nhất quán.
> Chương 10 `use-computer-while-calling` đã phát triển thành kho độc lập được duy trì liên tục [19PINE-AI/TalkAct](https://github.com/19PINE-AI/TalkAct); kho này chỉ giữ một tài liệu mô tả trỏ tới nó (`chapter10/use-computer-while-calling/README.md`).

**Các thí nghiệm phụ thuộc phần cứng thật / môi trường bên ngoài (không có mã trong kho này, trỏ tới tài liệu upstream):**

- **Thí nghiệm 9-8 / 9-9 · Điều khiển từ xa XLeRobot và điều khiển bằng LLM Agent**: cần cánh tay robot SO-100/XLeRobot, thao tác theo tài liệu upstream — [Teleop](https://xlerobot.readthedocs.io/en/latest/software/getting_started/XLeRobot_teleop.html) · [LLM Agent](https://xlerobot.readthedocs.io/en/latest/software/getting_started/LLM_agent.html)
- **Thí nghiệm 9-10 · Gắp vật RGB zero-shot Sim2Real**: [`StoneT2000/lerobot-sim2real`](https://github.com/StoneT2000/lerobot-sim2real) (phần huấn luyện mô phỏng có thể hoàn thành chỉ bằng GPU; triển khai thật cần cánh tay robot SO-100)
- **Thí nghiệm 6-11 · Đánh giá mô phỏng OpenVLA + RoboTwin2**: phụ thuộc huấn luyện/môi trường VLA xem README của `chapter7/SimpleVLA-RL` (trong đó giải thích cách lấy và cấu hình OpenVLA, RoboTwin2)

**Thí nghiệm dạng bài tập cho độc giả (trong sách đưa ra như bài tập, tái sử dụng các dự án đã được tài liệu hóa, không có thư mục riêng):**

- **Thí nghiệm 5-12 · Agent có thể tạo Agent**: tự mở rộng dựa trên `chapter5/coding-agent`
- **Thí nghiệm 6-2 / 6-3 / 6-4 / 6-9**: lần lượt là benchmark thủ công, đánh giá bộ nhớ, JSON Cards vs RAG, chọn phương án bộ nhớ — cải tạo và tái sử dụng các dự án chương 3 như `user-memory` / `user-memory-evaluation` / `contextual-retrieval`
- **Thí nghiệm 7-8 · Prompt distillation**: triển khai thực tế nằm ở chương 8 `chapter8/prompt-distillation` (tái sử dụng xuyên chương)
- **Thí nghiệm 7-9 · CoT distillation `[mở rộng]`**: sách đưa ra thiết kế thí nghiệm và tiêu chuẩn nghiệm thu, là thí nghiệm mở rộng cho độc giả; hiện chưa có mã riêng

## 🤝 Đóng góp

Sách và mã đi kèm đều là mã nguồn mở; rất hoan nghênh cộng đồng cùng xây dựng thông qua Pull Request. Chúng tôi đặc biệt hoan nghênh các loại đóng góp sau:

1. **Cải thiện nội dung sách**: sửa lỗi, bổ sung, diễn đạt rõ hơn, hoặc thêm tiến triển tiên phong mới (nội dung tiếng Việt xem `book-vi/chapter*.vi.md`)
2. **Cải thiện mã và sửa Bug**: giúp các dự án đi kèm vững chắc hơn, dễ dùng hơn và gần thực tiễn sản xuất hơn
3. **Dự án thực hành mới**: bổ sung/thay thế triển khai tốt hơn cho một thí nghiệm, hoặc đóng góp dự án ví dụ hoàn toàn mới
4. **Cải thiện thiết kế hình minh họa của sách**: làm cho biểu đồ trong `book-vi/images/` rõ ràng và đẹp hơn
5. **Bản dịch sang ngôn ngữ mới**: hoan nghênh dịch sách sang thêm nhiều ngôn ngữ — tham khảo cách tổ chức của các bản tiếng Anh (`book-en/`), Tamil (`book-ta/`) và tiếng Việt (`book-vi/`)

Trước khi gửi, khuyến nghị tự chạy các thí nghiệm liên quan để xác nhận có thể tái hiện; cũng hoan nghênh mở issue trước để thảo luận ý tưởng.

## 📄 Giấy phép

Dự án này được mở nguồn theo [Apache License 2.0](LICENSE); xem chi tiết trong file [`LICENSE`](LICENSE). Một số dự án con có thể chứa thông tin giấy phép riêng, vui lòng ưu tiên theo mô tả trong dự án con.

## ⭐ Star History

<a href="https://star-history.com/#bojieli/ai-agent-book&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/star-history-dark.png" />
    <source media="(prefers-color-scheme: light)" srcset="assets/star-history-light.png" />
    <img alt="Star History Chart" src="assets/star-history-light.png" width="720" />
  </picture>
</a>

<sub>Biểu đồ được vẽ bởi [`scripts/gen_star_history.py`](scripts/gen_star_history.py) (bắt đầu từ ngày 15 tháng 7 năm 2026), được [tác vụ theo lịch của GitHub Actions](.github/workflows/star-history.yml) tự động cập nhật mỗi ngày và commit vào thư mục <code>assets/</code>; nhấp vào biểu đồ để xem dữ liệu thời gian thực trên star-history.com.</sub>
