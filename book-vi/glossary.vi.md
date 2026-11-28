# Bảng thuật ngữ Anh - Việt {.unnumbered}

Bản dịch tiếng Việt ưu tiên **giữ thuật ngữ kỹ thuật chính bằng tiếng Anh** và thêm chú thích tiếng Việt ở lần xuất hiện quan trọng, thay vì dịch sát chữ gây khó hiểu. Các thuật ngữ dưới đây được dùng thống nhất trong bản dịch:

| Thuật ngữ | Cách dùng trong bản dịch | Chú thích ngắn |
| --- | --- | --- |
| Agent | Agent | Hệ thống AI có thể lập kế hoạch, gọi công cụ và lặp theo kết quả quan sát. |
| LLM | LLM / Large Language Model | Mô hình ngôn ngữ lớn, phần “bộ não” ra quyết định của Agent. |
| Context | ngữ cảnh / context | Toàn bộ thông tin mô hình nhìn thấy trong một lần gọi: system prompt, lịch sử hội thoại, tool schema, kết quả công cụ, bộ nhớ, v.v. |
| Context Engineering | Context Engineering (kỹ thuật ngữ cảnh) | Thiết kế và quản lý toàn bộ thông tin đưa vào context; rộng hơn prompt engineering. |
| Prompt Engineering | Prompt Engineering (kỹ thuật prompt) | Tối ưu chỉ dẫn ngôn ngữ tự nhiên cho mô hình. |
| Skill | Skill / Agent Skills | Gói chỉ dẫn, script và tài liệu chuyên môn mà Agent chỉ nạp vào context khi cần; Skill Hub là nơi phân phối Skill. |
| Agent status bar | thanh trạng thái Agent | Khối thông tin trạng thái (tiến độ, todo, tài nguyên) đặt ở cuối context để Agent bám sát nhiệm vụ. |
| Context compression | nén ngữ cảnh | Tóm lược, cắt bớt hoặc chuyển ra ngoài phần context cũ khi trajectory quá dài. |
| Harness | Harness | Lớp hạ tầng bên ngoài mô hình: context, tools, constraints, verification, correction, logging, permission, retry, guardrails. Không dịch là “khai thác”. |
| Harness Engineering | Harness Engineering (kỹ thuật Harness) | Thiết kế lớp hạ tầng bao quanh mô hình để biến năng lực mô hình thành hệ thống đáng tin cậy. |
| Graph Engineering | Graph Engineering (kỹ thuật đồ thị) | Góc nhìn điều phối Agent như một đồ thị gồm nút, cạnh và trạng thái. |
| Tool calling | tool calling / gọi công cụ | Cơ chế để LLM gọi hàm hoặc công cụ bên ngoài theo cấu trúc. |
| Function calling | function calling | Một dạng tool calling qua API. |
| MCP, A2A | MCP (Model Context Protocol), A2A | Giao thức mở: MCP nối Agent với công cụ và dữ liệu; A2A nối Agent với Agent của tổ chức khác. |
| ReAct | ReAct | Vòng lặp Reasoning + Acting: suy nghĩ, hành động, quan sát rồi lặp lại. |
| Trajectory | trajectory | Chuỗi lịch sử chạy của Agent: user message, model response, tool call, tool result. |
| Observation | observation | Kết quả Agent quan sát được sau một hành động hoặc tool call. |
| Action Space | Action Space | Tập hợp hành động/công cụ mà Agent có thể thực hiện. |
| Observation Space | Observation Space | Tập hợp thông tin Agent có thể quan sát. |
| Policy | Policy | Chiến lược ra quyết định trong RL; ánh xạ observation sang action. |
| Post-training | post-training | Các bước sau pretraining như SFT/RL để tinh chỉnh hành vi mô hình. |
| SFT | SFT / supervised fine-tuning | Fine-tuning có giám sát bằng dữ liệu mẫu. |
| RL | RL / reinforcement learning | Học tăng cường bằng reward từ môi trường hoặc verifier. |
| Mid-training | Mid-training | Huấn luyện tiếp trên phân phối đích (lĩnh vực, ngôn ngữ, năng lực) giữa pretraining và SFT/RL. |
| Rollout | rollout | Một lần Agent chạy trọn nhiệm vụ để sinh trajectory cho huấn luyện hoặc đánh giá. |
| On-policy | on-policy / off-policy | Dữ liệu do chính policy hiện tại sinh ra / do policy khác sinh ra. |
| Reward | phần thưởng (reward) | Tín hiệu học trong RL; mô hình lách tiêu chí để ăn điểm gọi là reward hacking. |
| Credit assignment | phân bổ tín dụng (credit assignment) | Xác định bước nào trong trajectory nhiều lượt góp phần vào kết quả cuối. |
| Distillation | chưng cất (distillation) | Dùng mô hình thầy giám sát mô hình trò; on-policy distillation chấm trên chính rollout của mô hình trò. |
| In-Context Learning | In-Context Learning (học trong ngữ cảnh) | Mô hình học tạm từ ví dụ/quy tắc nằm trong context mà không đổi trọng số. |
| External Learning | External Learning (học bên ngoài tham số mô hình) | Lưu tri thức/quy trình vào file, knowledge base, memory hoặc tool thay vì ghi vào trọng số mô hình. |
| Continual evolution | tiến hóa liên tục | Agent rút kinh nghiệm từ trajectory thành tri thức, chỉ dẫn, chương trình hoặc tham số; “học trong khi ngủ” là bước tổng hợp ngoại tuyến. |
| RAG | RAG / Retrieval-Augmented Generation | Truy xuất tài liệu liên quan rồi đưa vào context để mô hình trả lời. |
| Agentic RAG | Agentic RAG | RAG do Agent chủ động quyết định khi nào truy xuất và truy xuất gì. |
| KV Cache | KV Cache | Bộ nhớ đệm key/value của transformer giúp tái sử dụng phần prefix đã tính. |
| Prompt injection | prompt injection | Tấn công tiêm chỉ dẫn độc hại vào prompt/context. |
| Guardrails | guardrails | Các lớp kiểm soát, ràng buộc, xác minh và chặn rủi ro. |
| Sidecar | Sidecar | Thành phần kiểm tra/phê duyệt chạy song song hoặc kèm Agent chính. |
| HITL | HITL / Human-in-the-Loop | Cơ chế có con người tham gia xác nhận hoặc phê duyệt. |
| Observability | observability | Khả năng quan sát hệ thống qua log, trace, metric, audit trail. |
| Pass@k / Pass^k | Pass@k / Pass^k | Pass@k: ít nhất một trong $k$ lần chạy thành công (trần năng lực); Pass^k: cả $k$ lần đều thành công (độ tin cậy). |
| Verifier | bộ kiểm chứng (verifier) | Chương trình hoặc mô hình phán định kết quả có thật sự đạt yêu cầu hay không. |
| LLM-as-a-Judge | LLM-as-a-Judge | Dùng LLM chấm điểm theo rubric khi thiếu tiêu chí tất định. |
| Artifact | artifact | Sản phẩm trung gian/cuối cùng do Agent tạo ra: file, SQL, slide, video, report. |
| Vibe coding | vibe coding | Cách làm việc/lập trình với AI bằng mô tả ý định, thảo luận và để Agent triển khai; trong sách có nhấn mạnh dùng giọng nói. |
| Event-driven | bất đồng bộ, hướng sự kiện | Agent được sự kiện bên ngoài (email, tin nhắn, hẹn giờ) đánh thức thay vì chỉ chờ người dùng hỏi. |
| Full-duplex | full-duplex | Tương tác giọng nói nghe và nói cùng lúc, cho phép ngắt lời; đối lập với cascade và mô hình theo lượt. |
| Computer Use | Computer Use | Agent thao tác GUI/trình duyệt/máy tính như người dùng. |
| Grounding | định vị thị giác (grounding) | Ánh xạ mô tả bằng lời sang đúng vị trí phần tử trên màn hình. |
| VLA | VLA (Vision-Language-Action) | Mô hình nhận hình ảnh và chỉ dẫn, xuất thẳng lệnh điều khiển robot. |
| World model | mô hình thế giới (world model) | Mô hình dự đoán trạng thái kế tiếp của môi trường khi thực hiện một hành động. |
| Multi-agent | multi-agent | Hệ thống nhiều Agent phối hợp hoặc phân vai. |
| Sub-agent | Agent con / sub-agent | Agent được Agent chính giao việc, chạy trong context riêng và trả về kết quả gọn. |
| Comprehension debt | nợ hiểu biết, đầu hàng nhận thức | Kỹ sư mất dần hiểu biết về hệ thống do Agent viết, rồi buông luôn việc phán đoán cho Agent. |
