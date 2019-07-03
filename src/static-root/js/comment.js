
$(function(){
  // // 도큐먼트가 로드 되었을때 실행됨
  // // 여기에서 스피너를 업새면 됩니다.
  // setTimeout(function(){
  //   $('#preloader').css('display', 'none');
  //   $('#body').css('display', 'block');

    
  // }, 1000);

  document.getElementById('commentBtn').addEventListener('click', function(){
    // 댓글 입력 버튼이 클릭되었을 때, 카드에 댓글을 추가시킨다.
    let comment = $('#comment').val();
    let commentArea = $('#comment-area');
    let newComment = `
      <li class="list-group-item">` + comment + `</li>
    `;
    commentArea.append(newComment);
    $('#commentModal').modal('hide');
  })
})