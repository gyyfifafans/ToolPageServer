function get_auth_code(){
    var phone = $("#auth_code").val();
    $.ajaxSettings.async = false;
    if(phone){
        $.get("/getAuthCode?phone="+phone,function(data){
            results = JSON.parse(data);
            var trHtml = "";
            $(".code").empty();
            for(var key in results){
                if(results[key]==null){
                    trHtml+='<li>'+key+' :  '+'------</li><br/>'
                }
                else{
                    trHtml+='<li>'+key+' :  '+results[key]+'</li><br/>'
                }
                            
            }
            $(".code").append(trHtml);
        });
    }
    else{
        alert("请输入手机号 ！！");
        }

}

function get_reset_code(){
    var id_no = $("#id_no").val();
    $.ajaxSettings.async = false;
    if(id_no){
        $.get("/getResetTradeCode?id_no="+id_no,function(data){
            results = JSON.parse(data);
            var trHtml = "";
            $(".reset_code").empty();
            for(var key in results){
                if(results[key]==null){
                    trHtml+='<li>'+key+' :  '+'------</li><br/>'
                }
                else{
                    trHtml+='<li>'+key+' :  '+results[key]+'</li><br/>'
                }
                            
            }
            $(".reset_code").append(trHtml);
        });
    }
    else{
        alert("请输入身份证号或者护照号 ！！");
    }


}
