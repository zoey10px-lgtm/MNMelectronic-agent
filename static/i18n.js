/* Translate interface text while preserving form values and customer content. */
(() => {
  'use strict';
  const rows = `회사소개|Company|Giới thiệu
제품소개|Products|Sản phẩm
기술·품질|Technology & Quality|Công nghệ & Chất lượng
고객지원|Customer Support|Hỗ trợ khách hàng
관리자|Admin|Quản trị
품질 문의|Quality Inquiry|Yêu cầu chất lượng
작은 디테일이|Small details|Những chi tiết nhỏ
큰 차이|a big difference|sự khác biệt lớn
를 만듭니다.|make it happen.|tạo nên giá trị.
정밀한 부품에서 시작되는 더 나은 가능성.|Better possibilities begin with precision components.|Khả năng tốt hơn bắt đầu từ linh kiện chính xác.
우리는 모든 연결과 마감에 신뢰를 담습니다.|Trust in every connection and finish.|Tin cậy trong từng kết nối và bề mặt hoàn thiện.
제품 살펴보기|Explore Products|Khám phá sản phẩm
M&M 알아보기|Discover M&M|Khám phá M&M
눈에 보이지 않는|Precision even in|Chính xác ngay cả ở
부분까지,|the smallest details,|những chi tiết nhỏ nhất,
정밀하게.|with care.|với sự tận tâm.
우리가 만드는 것은 제품을 구성하는 작은 금속 부품입니다. 작은 차이가 조립의 완성도와 제품의 신뢰를 결정한다고 믿습니다.|We make the small metal components that support your products. Every detail contributes to assembly quality and product reliability.|Chúng tôi sản xuất các linh kiện kim loại nhỏ cho sản phẩm của bạn. Mỗi chi tiết đóng góp vào chất lượng lắp ráp và độ tin cậy.
회사 소개 자세히 보기|More About Us|Tìm hiểu công ty
작은 부품,|Small components,|Linh kiện nhỏ,
큰 역할.|essential roles.|vai trò lớn.
전체 제품 보기|View All Products|Xem tất cả sản phẩm
신뢰할 수 있는 품질은|Quality you can trust|Chất lượng đáng tin cậy
검증할 수 있는 기록|verifiable records|hồ sơ có thể xác minh
에서.|at every step.|trong từng bước.
제품 정보와 검사 기준, 고객 문의를 연결합니다.|Connecting products, inspection criteria, and customer inquiries.|Kết nối sản phẩm, tiêu chí kiểm tra và yêu cầu khách hàng.
현상을 빠르게 확인하고 책임 있는 해결로 이어갑니다.|From fast inspection to responsible resolution.|Từ kiểm tra nhanh đến giải quyết có trách nhiệm.
M&M 품질 철학|Our Quality Philosophy|Triết lý chất lượng
기술의 시작은 정밀함,|Technology begins with precision,|Công nghệ bắt đầu từ sự chính xác,
그 완성은|and comes together through|và hoàn thiện bằng
신뢰.|trust.|niềm tin.
정밀함|Precision|Chính xác
작은 형태와 마감에도 분명한 기준을 적용합니다.|Clear standards for every shape and finish.|Tiêu chuẩn rõ ràng cho từng hình dạng và bề mặt.
추적성|Traceability|Truy xuất nguồn gốc
제품 모델부터 검사·문의 이력까지 체계적으로 연결합니다.|Linking product models with inspections and inquiry histories.|Liên kết mẫu sản phẩm với kiểm tra và lịch sử yêu cầu.
책임 있는 대응|Responsible Support|Hỗ trợ có trách nhiệm
문제를 기록하는 데 그치지 않고 해결 과정까지 관리합니다.|We document issues and manage their resolution.|Ghi nhận vấn đề và quản lý quá trình giải quyết.
제품에 문제가 생겼나요?|Need help with a product?|Bạn cần hỗ trợ về sản phẩm?
함께 해결하겠습니다.|Let us help you resolve it.|Hãy cùng giải quyết.
품질지원 문의|Contact Quality Support|Liên hệ hỗ trợ chất lượng
정밀함을 완성하는|Precision connected|Kết nối sự chính xác
품질로 이어지는 연결.|through quality.|với chất lượng.
신뢰를 만드는 기술,|Technology that builds trust,|Công nghệ tạo dựng niềm tin,
고객 품질지원까지.|through customer support.|đến hỗ trợ khách hàng.
M&M Electronics는 전자기기용 정밀 금속 부품을 중심으로 소재, 형상, 품질 확인과 고객 대응 과정을 연결하는 기업형 서비스 콘셉트입니다.|M&M Electronics connects precision metal components with inspection, quality records, and customer support in an enterprise service concept.|M&M Electronics kết nối linh kiện kim loại chính xác với kiểm tra, hồ sơ chất lượng và hỗ trợ khách hàng trong mô hình dịch vụ doanh nghiệp.
작은 디테일을 연결해|Connecting small details|Kết nối những chi tiết nhỏ
더 큰 가능성을 만듭니다.|to create greater possibilities.|để tạo ra khả năng lớn hơn.
제품에서 확인된 현상을 기록하고, 담당자가 판단 근거를 확인해 후속 조치로 이어지는 환경을 지향합니다.|Record product observations, review the evidence, and coordinate follow-up actions.|Ghi nhận hiện tượng trên sản phẩm, xem xét bằng chứng và phối hợp xử lý tiếp theo.
정밀 금속 부품에서|From precision metal parts|Từ linh kiện kim loại chính xác
네 가지 모델.|Four product models.|Bốn mẫu sản phẩm.
* 제품 모델 코드는 제공된 브래킷 참고 자료에서 가져왔습니다. 세부 사양과 기술 이미지는 시연용 표현입니다.|* Model codes come from the supplied bracket references. Specifications and technical illustrations are demonstration content.|* Mã sản phẩm lấy từ tài liệu giá đỡ được cung cấp. Thông số và hình minh họa dùng cho trình diễn.
품질에 대한 대답은|Quality answers begin|Câu trả lời về chất lượng bắt đầu
명확한 근거로부터.|with clear evidence.|từ bằng chứng rõ ràng.
연결된 정보, 확인 가능한 판단, 책임 있는 후속 조치.|Connected information, verifiable decisions, responsible follow-up.|Thông tin liên kết, quyết định có thể xác minh, xử lý có trách nhiệm.
제품 및 LOT 식별|Product & LOT Identification|Nhận dạng sản phẩm & LOT
고객이 제보한 제품 코드와 LOT 번호를 확인해 관련 데이터를 연결합니다.|Connect relevant records using the product code and LOT number.|Kết nối hồ sơ bằng mã sản phẩm và số LOT.
이미지 관찰|Image Review|Xem xét hình ảnh
이미지에서 확인할 수 있는 현상과 추가 측정이 필요한 사항을 구분합니다.|Distinguish visible observations from items requiring measurement.|Phân biệt hiện tượng nhìn thấy và nội dung cần đo bổ sung.
관련 사례 검토|Reference Review|Xem xét trường hợp tham khảo
과거 민원 유형, 품질 기준, 처리 사례를 찾아 담당자가 검토할 수 있도록 구성합니다.|Retrieve inquiry types, quality references, and previous cases for review.|Truy xuất loại yêu cầu, tài liệu chất lượng và trường hợp trước để xem xét.
조치 및 이력 관리|Actions & History|Hành động & Lịch sử
권장 조치와 담당자 확인 결과를 연결해 반복되는 문제에 대응합니다.|Link recommended actions with reviewer findings to address recurring issues.|Liên kết hành động đề xuất với kết quả kiểm tra để xử lý vấn đề lặp lại.
판단은 투명하게,|Clear decisions,|Quyết định minh bạch,
해결은 구체적으로.|practical resolutions.|giải pháp cụ thể.
YOLO의 결함 의심 위치와 등록 사진의 라벨 해석을 함께 제공합니다. 원인과 최종 조치는 담당자가 검사 기준에 따라 확인합니다.|YOLO locations and reference labels support inspection. A reviewer confirms causes and final actions using inspection criteria.|Vị trí YOLO và nhãn tham khảo hỗ trợ kiểm tra. Nhân viên xác nhận nguyên nhân và biện pháp theo tiêu chí kiểm tra.
품질 문의 시작하기|Start a Quality Inquiry|Bắt đầu yêu cầu chất lượng
문제의 순간부터,|From the first issue|Từ lúc phát hiện vấn đề
해결의 다음 단계까지.|to the next step toward resolution.|đến bước giải quyết tiếp theo.
제품 정보와 현상을 남겨주세요. 문의를 정리하고 담당자에게 전달하는 과정을 한곳에서 확인할 수 있습니다.|Share the product details and symptoms. Review and submit your inquiry in one place.|Cung cấp thông tin sản phẩm và hiện tượng. Xem xét và gửi yêu cầu tại một nơi.
고객 품질지원 센터|Quality Support Center|Trung tâm hỗ trợ chất lượng
품질 문의 접수|Submit Quality Inquiry|Gửi yêu cầu chất lượng
접수 내역 조회|Track Inquiry|Tra cứu yêu cầu
최종 접수한 문의는 실행 중인 서버에 저장됩니다|Submitted inquiries are saved on the server|Yêu cầu đã gửi được lưu trên máy chủ
품질 문의 작성|Your Quality Inquiry|Nội dung yêu cầu chất lượng
정확한 확인을 위해 제품과 문제 상황을 알려주세요.|Tell us about the product and issue.|Cho chúng tôi biết sản phẩm và vấn đề.
제품 모델|Product Model|Mẫu sản phẩm
사진에서 모델 자동 추정|Identify Model from Photo|Nhận dạng mẫu từ ảnh
제품을 선택해주세요|Select a product|Chọn sản phẩm
LOT 번호|LOT Number|Số LOT
(선택)|(Optional)|(Không bắt buộc)
문의 유형|Inquiry Type|Loại yêu cầu
문의 유형을 선택해주세요|Select an inquiry type|Chọn loại yêu cầu
표면 스크래치|Surface Scratch|Vết xước bề mặt
찍힘·변형|Dent / Deformation|Móp / Biến dạng
균열 의심|Suspected Crack|Nghi nứt
치수·조립 문제|Dimensions / Assembly|Kích thước / Lắp ráp
도장·코팅 불량|Paint / Coating|Sơn / Lớp phủ
이물질·오염|Foreign Material / Contamination|Dị vật / Nhiễm bẩn
배송·포장 문제|Shipping / Packaging|Vận chuyển / Đóng gói
기타 문의|Other Inquiry|Yêu cầu khác
불만 및 증상 내용|Issue and Symptoms|Vấn đề và hiện tượng
(사진 첨부 시 선택)|(Optional with photos)|(Không bắt buộc khi có ảnh)
현상이 발생한 상황과 원하는 조치를 자세히 적어주세요.|Describe when the issue occurred and what help you need.|Mô tả hoàn cảnh phát sinh và hỗ trợ bạn cần.
불량 제품 사진|Product Photos|Ảnh sản phẩm
(선택 · 최대 3장)|(Optional · Up to 3)|(Không bắt buộc · Tối đa 3 ảnh)
이미지를 이곳에 끌어오거나 선택하세요|Drop images here or select files|Kéo ảnh vào đây hoặc chọn tệp
JPG, PNG, WEBP · 각 파일 최대 5MB|JPG, PNG, WEBP · Up to 5MB each|JPG, PNG, WEBP · Tối đa 5MB mỗi ảnh
사진 선택하기|Select Photos|Chọn ảnh
담당자 성함|Contact Name|Tên người liên hệ
이메일|Email|Email
사진·문의 분석하기|Analyze Photos & Inquiry|Phân tích ảnh & yêu cầu
사진에서 결함 의심 위치와 유형을 분석합니다. 사진을 올리면 문의 내용은 생략할 수 있습니다.|Analyze suspected defect locations and types. A written message is optional when photos are attached.|Phân tích vị trí và loại lỗi nghi ngờ. Có thể bỏ trống nội dung khi đính kèm ảnh.
사진 분석과 문의 진행|Analysis & Inquiry|Phân tích & Yêu cầu
접수 전 확인부터 최종 접수까지 안내합니다.|Review the findings and submit your inquiry.|Xem kết quả và gửi yêu cầu.
안녕하세요. M&M Electronics 품질지원 센터입니다.|Welcome to M&M Electronics Quality Support.|Chào mừng đến với bộ phận hỗ trợ chất lượng M&M Electronics.
제품을 선택하고 근접 사진을 올리면 결함 의심 위치와 유형, 확인할 사항을 안내합니다. 문의 내용은 사진과 함께 또는 별도로 작성할 수 있습니다.|Select a product and upload close-up photos to review suspected defects and next checks. You can also submit a written inquiry.|Chọn sản phẩm và tải ảnh cận cảnh để xem lỗi nghi ngờ và nội dung cần kiểm tra. Bạn cũng có thể gửi yêu cầu bằng văn bản.
상담 준비 완료|Ready to assist|Sẵn sàng hỗ trợ
문의 내용 입력|Describe Your Inquiry|Nhập yêu cầu
접수 전 검토|Review Before Submission|Xem xét trước khi gửi
관리자 전달|Submit for Review|Chuyển đến quản trị
메시지는 왼쪽 문의 입력란에 작성해주세요.|Write your message in the inquiry form.|Nhập nội dung trong biểu mẫu yêu cầu.
최종 접수한 문의와 사진 검사 결과는 실행 중인 서버에 저장됩니다.|Submitted inquiries and inspection results are saved on the server.|Yêu cầu và kết quả kiểm tra được lưu trên máy chủ.
문의 처리 현황 조회|Track Your Inquiry|Tra cứu trạng thái yêu cầu
접수 완료 시 발급된 접수번호를 입력해주세요.|Enter the inquiry number issued after submission.|Nhập mã yêu cầu được cấp sau khi gửi.
조회하기|Track|Tra cứu
접수된 고객 문의를 체계적으로 확인하고|Review customer inquiries|Xem xét yêu cầu khách hàng
담당자의 다음 조치를 이어갑니다.|and coordinate the next action.|và phối hợp bước xử lý tiếp theo.
홈페이지로 돌아가기|Back to Home|Về trang chủ
관리자 로그인|Admin Login|Đăng nhập quản trị
관리자 계정으로 로그인하여 민원 처리 현황을 확인하세요.|Sign in to manage customer inquiries.|Đăng nhập để quản lý yêu cầu khách hàng.
아이디|Username|Tên đăng nhập
비밀번호|Password|Mật khẩu
로그인|Sign In|Đăng nhập
로컬 실행용 초기 계정입니다. 설정 파일에서 계정을 변경할 수 있습니다.|Use the administrator credentials configured for this server.|Sử dụng tài khoản quản trị đã cấu hình cho máy chủ.
대시보드|Dashboard|Bảng điều khiển
민원 접수 관리|Inquiry Management|Quản lý yêu cầu
유형별 통계|Category Statistics|Thống kê theo loại
로그아웃|Sign Out|Đăng xuất
관리자 대시보드|Admin Dashboard|Bảng điều khiển quản trị
오늘의 품질 문의를|Today's quality inquiries,|Yêu cầu chất lượng hôm nay,
한눈에 관리하세요.|all in one place.|tất cả tại một nơi.
고객이 최종 접수한 민원이 자동으로 목록에 표시됩니다.|Submitted inquiries appear automatically.|Yêu cầu đã gửi tự động xuất hiện.
최근 접수된 민원|Recent Inquiries|Yêu cầu gần đây
전체 보기 ↗|View All ↗|Xem tất cả ↗
유형별 접수 현황|Inquiries by Category|Yêu cầu theo loại
불만 유형|Issue Type|Loại vấn đề
CSV 내보내기|Export CSV|Xuất CSV
전체 상태|All Statuses|Tất cả trạng thái
접수 완료|Received|Đã tiếp nhận
검토 중|Under Review|Đang xem xét
조치 중|In Progress|Đang xử lý
처리 완료|Resolved|Đã giải quyết
보류|On Hold|Tạm dừng
접수번호|Inquiry Number|Mã yêu cầu
제품 / LOT|Product / LOT|Sản phẩm / LOT
접수 일시|Received At|Thời gian tiếp nhận
처리 상태|Status|Trạng thái
민원 유형 분석|Inquiry Analysis|Phân tích yêu cầu
최종 접수된 문의를 기준으로 집계한 통계입니다.|Statistics include confirmed inquiries.|Thống kê bao gồm các yêu cầu đã xác nhận.
유형별 민원 건수|Inquiry Counts by Category|Số yêu cầu theo loại
민원 상세 보기|Inquiry Details|Chi tiết yêu cầu
정식으로 문의를 접수할까요?|Submit this inquiry?|Gửi yêu cầu này?
접수하면 관리자 대시보드에 문의 내용과 첨부된 사진이 등록됩니다. 접수 후에도 처리 상태를 조회할 수 있어요.|Your inquiry and photos will be available to administrators. You can track its status after submission.|Yêu cầu và ảnh sẽ được chuyển đến quản trị viên. Bạn có thể theo dõi trạng thái sau khi gửi.
돌아가기|Go Back|Quay lại
문의 최종 접수|Submit Inquiry|Gửi yêu cầu
Hackathon UI prototype · 기업 정보와 제품 설명은 시연용 콘셉트입니다.|Hackathon prototype · Company and product descriptions are demonstration concepts.|Nguyên mẫu hackathon · Thông tin công ty và sản phẩm dùng cho trình diễn.
AI 문의 분석 및 답변 초안|AI Review & Reply Draft|Phân tích AI & Bản nháp phản hồi
다음 확인 사항|Next Checks|Nội dung kiểm tra tiếp theo
AI가 작성한 검토용 초안입니다.|AI-generated draft for review.|Bản nháp do AI tạo để xem xét.
사진 분석 결과|Photo Inspection Results|Kết quả kiểm tra ảnh
사진 검사 결과가 없습니다.|No photo inspection results.|Chưa có kết quả kiểm tra ảnh.
확인할 내용|Recommended Checks|Nội dung cần kiểm tra
등록된 원본 자료와 비교|Compare with Registered Reference|So sánh với tài liệu đã đăng ký
검사 위치 안내도입니다. 제품 사진을 올려주세요.|This is an inspection map. Upload a product photo.|Đây là sơ đồ kiểm tra. Vui lòng tải ảnh sản phẩm.
결함 위치와 유형을 판별하지 못했습니다. 이 결과로 정상 여부를 결정할 수 없습니다.|No defect location or type was identified. Physical review is needed to assess the part.|Chưa xác định được vị trí hoặc loại lỗi. Cần kiểm tra thực tế để đánh giá linh kiện.
검출된 영역이 없습니다. 정상 판정은 아니며 담당자 확인이 필요합니다.|No regions were detected. A reviewer must assess the part.|Chưa phát hiện vùng lỗi. Nhân viên cần kiểm tra linh kiện.
사진이 없어 이미지 검사를 진행하지 않았습니다.|No photo was attached for image inspection.|Không có ảnh đính kèm để kiểm tra.
등록 원본 자료 보기 ↗|View Registered References ↗|Xem tài liệu đã đăng ký ↗
등록 라벨 사진으로 확인하기|Try a Registered Reference Photo|Thử ảnh tham khảo đã đăng ký
선택한 사진 넣기|Use Selected Photo|Dùng ảnh đã chọn
전체 원본 31개의 라벨·해석 보기 ↗|View Labels for All 31 Originals ↗|Xem nhãn của toàn bộ 31 ảnh gốc ↗
사진을 올리면 결함 위치·유형을 예측합니다. 등록 사진의 정답 자료는 결과 아래에서 비교할 수 있습니다.|Upload a photo to predict defect locations and types. Registered labels are available for comparison.|Tải ảnh để dự đoán vị trí và loại lỗi. Có thể so sánh với nhãn ảnh đã đăng ký.
첨부한 사진에서 결함 의심 부위를 검사하고 있습니다. 잠시 기다려주세요.|Inspecting the photos and preparing the reply. Please wait.|Đang kiểm tra ảnh và chuẩn bị phản hồi. Vui lòng đợi.
검사 결과를 확인해주세요.|Please review the results.|Vui lòng xem kết quả.
정식 문의 접수|Submit Inquiry|Gửi yêu cầu
를 누르면 관리자에게 전달됩니다.|to send it to the administrator.|để chuyển đến quản trị viên.
내용 수정하기|Edit Inquiry|Sửa yêu cầu
전체 접수|All Inquiries|Tất cả yêu cầu
누적 접수 건수|Total inquiries|Tổng số yêu cầu
접수 대기|Awaiting Review|Chờ xem xét
담당자 확인 필요|Awaiting a reviewer|Chờ nhân viên xác nhận
처리 진행|In Progress|Đang xử lý
검토·조치 진행 중|Review and action in progress|Đang xem xét và xử lý
완료된 민원|Resolved inquiries|Yêu cầu đã giải quyết
기본 접수 정보|Inquiry Information|Thông tin yêu cầu
미입력|Not Provided|Chưa cung cấp
담당자|Contact|Người liên hệ
접수 시간|Received At|Thời gian tiếp nhận
고객 불만 내용|Customer Message|Nội dung khách hàng
AI 분석 및 권장 조치|AI Analysis & Recommended Actions|Phân tích AI & Hành động đề xuất
기본 검토 절차|Review Process|Quy trình xem xét
처리 상태 관리|Manage Status|Quản lý trạng thái
현재 처리 상태|Current Status|Trạng thái hiện tại
우선순위|Priority|Mức ưu tiên
낮음|Low|Thấp
보통|Normal|Bình thường
높음|High|Cao
긴급|Urgent|Khẩn cấp
변경 사항 저장|Save Changes|Lưu thay đổi
저장 즉시 목록과 통계에 반영됩니다.|Changes immediately update the list and statistics.|Thay đổi cập nhật ngay danh sách và thống kê.
처리 이력|Activity History|Lịch sử xử lý
변경 이력이 없습니다.|No changes yet.|Chưa có thay đổi.
제품|Product|Sản phẩm
유형|Category|Loại
사진|Photos|Ảnh
LOT 미입력|No LOT Provided|Chưa cung cấp LOT
학습에 사용한 사진|Training Photo|Ảnh huấn luyện
학습에서 제외한 검증 사진|Validation Photo|Ảnh kiểm định
검토 자료|Reference Material|Tài liệu tham khảo
등록 자료의 라벨입니다. 위 모델 예측과 비교할 수 있습니다.|These are registered labels for comparison with the model predictions.|Đây là nhãn đã đăng ký để so sánh với dự đoán mô hình.
미식별|Unidentified|Chưa nhận dạng
사진은 최대 3장까지 첨부할 수 있습니다.|Attach up to 3 photos.|Đính kèm tối đa 3 ảnh.
사진은 장당 최대 5MB까지 가능합니다.|Each photo must be 5MB or smaller.|Mỗi ảnh không quá 5MB.
제품을 선택하고 사진 또는 10자 이상의 문의 내용을 입력해주세요.|Select a product and attach a photo or a message of at least 10 characters.|Chọn sản phẩm và đính kèm ảnh hoặc nội dung ít nhất 10 ký tự.
이메일 형식을 확인해주세요.|Check the email address.|Kiểm tra địa chỉ email.
최종 접수가 완료되었습니다.|Your inquiry was submitted.|Đã gửi yêu cầu.
관리자로 로그인했습니다.|Signed in as administrator.|Đã đăng nhập quản trị.
처리 상태가 저장되었습니다.|Status saved.|Đã lưu trạng thái.
먼저 문의 내용을 입력해주세요.|Enter your inquiry first.|Vui lòng nhập yêu cầu trước.
입력창에서 수정한 뒤 다시 분석해주세요.|Edit the form and analyze it again.|Sửa biểu mẫu và phân tích lại.
관리자 아이디|Administrator Username|Tên đăng nhập quản trị
홍길동|Your name|Tên của bạn
예: LOT-2026-001|Example: LOT-2026-001|Ví dụ: LOT-2026-001
예: A176 제품에서 표면 스크래치가 발견되었습니다. 불량 위치와 교환 가능 여부를 확인하고 싶습니다.|Example: A scratch was found on an A176 part. Please review the location and available next steps.|Ví dụ: Phát hiện vết xước trên linh kiện A176. Vui lòng kiểm tra vị trí và hướng xử lý.
정밀 금속 브래킷 · A176 시리즈|Precision metal bracket · A176 series|Giá đỡ kim loại chính xác · Dòng A176
표면 및 체결 위치 품질 관리|Surface and mounting quality|Chất lượng bề mặt và vị trí lắp
장착용 금속 부품 · A376 시리즈|Metal mounting part · A376 series|Linh kiện lắp kim loại · Dòng A376
조립 안정성과 가공 품질 확인|Assembly stability and machining quality|Độ ổn định lắp ráp và chất lượng gia công
정밀 가공 프레임 · A156 시리즈|Precision frame · A156 series|Khung chính xác · Dòng A156
형상·가장자리 품질 관리|Shape and edge quality|Chất lượng hình dạng và cạnh
금속 지지 부품 · A276 시리즈|Metal support · A276 series|Chi tiết đỡ kim loại · Dòng A276
연결부 및 외관 품질 확인|Joint and appearance quality|Chất lượng mối nối và ngoại quan`;
  const translations = new Map(rows.split('\n').map(line => {
    const [ko, en, vi] = line.split('|'); return [ko, {ko, en, vi}];
  }));
  let language = 'ko';
  try { language = localStorage.getItem('mm-language') || 'ko'; } catch {}
  if (!['ko', 'en', 'vi'].includes(language)) language = 'ko';
  const originals = new WeakMap();
  const attributes = new WeakMap();
  function translate(text) {
    const direct = translations.get(text);
    if (direct) return direct[language];
    if (language === 'ko') return text;
    const pairs = language === 'en' ? [
      [/^사진 (\d+)$/, 'Photo $1'], [/^사진 기준 /, 'In the photo: '],
      [/^모델 예측 (\d+)곳$/, 'YOLO predictions: $1'],
      [/^검출 점수 /, 'Detection score: '], [/^제품 모델: /, 'Product model: '],
      [/^문의 관련 참고자료 (\d+)건$/, 'Related references: $1'],
      [/^검사 상세 · 낮은 점수 후보 (\d+)건$/, 'Inspection details · low-score candidates: $1'],
      [/^점수 /, 'Score '], [/^총 (\d+)건의 문의$/, 'Total inquiries: $1'],
      [/^첨부 제품 사진 \((\d+)장\)$/, 'Attached photos ($1)'],
      [/^YOLO가 결함 (\d+)곳을 검출하고 유형 (\d+)종을 예측했습니다\.$/, 'YOLO detected $1 regions across $2 defect types.']
    ] : [
      [/^사진 (\d+)$/, 'Ảnh $1'], [/^사진 기준 /, 'Trong ảnh: '],
      [/^모델 예측 (\d+)곳$/, 'Dự đoán YOLO: $1'],
      [/^검출 점수 /, 'Điểm phát hiện: '], [/^제품 모델: /, 'Mẫu sản phẩm: '],
      [/^문의 관련 참고자료 (\d+)건$/, 'Tài liệu tham khảo: $1'],
      [/^검사 상세 · 낮은 점수 후보 (\d+)건$/, 'Chi tiết kiểm tra · vùng điểm thấp: $1'],
      [/^점수 /, 'Điểm '], [/^총 (\d+)건의 문의$/, 'Tổng số yêu cầu: $1'],
      [/^첨부 제품 사진 \((\d+)장\)$/, 'Ảnh đính kèm ($1)'],
      [/^YOLO가 결함 (\d+)곳을 검출하고 유형 (\d+)종을 예측했습니다\.$/, 'YOLO phát hiện $1 vùng thuộc $2 loại lỗi.']
    ];
    for (const [pattern, replacement] of pairs) if (pattern.test(text)) return text.replace(pattern, replacement);
    return text;
  }
  function apply() {
    observer.disconnect();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement?.closest('script,style,textarea,.chat-message.user,.detail-message,[data-no-translate],#languageSelect')) continue;
      const cached = originals.get(node);
      const original = cached && node.nodeValue === cached.last ? cached.original : node.nodeValue;
      const key = original.trim();
      const next = key ? original.replace(key, translate(key)) : original;
      if (node.nodeValue !== next) node.nodeValue = next;
      originals.set(node, {original, last: next});
    }
    document.querySelectorAll('[placeholder], [aria-label]').forEach(element => {
      let values = attributes.get(element);
      if (!values) { values = {}; attributes.set(element, values); }
      for (const name of ['placeholder', 'aria-label']) {
        const value = element.getAttribute(name);
        if (value === null) continue;
        if (!values[name] || value !== values[name].last) values[name] = {original: value};
        const next = translate(values[name].original);
        if (next !== value) element.setAttribute(name, next);
        values[name].last = next;
      }
    });
    document.documentElement.lang = language;
    observer.observe(document.body, {childList: true, subtree: true, characterData: true});
  }
  let scheduled = false;
  const observer = new MutationObserver(() => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; apply(); });
  });
  const selector = document.querySelector('#languageSelect');
  if (selector) {
    selector.value = language;
    selector.addEventListener('change', () => {
      language = selector.value;
      try { localStorage.setItem('mm-language', language); } catch {}
      apply();
    });
  }
  window.mmTranslate = translate;
  apply();
})();
