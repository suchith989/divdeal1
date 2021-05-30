window.addEventListener('keydown',function(e)
{
	if(e.keyIdentifier=='U+000A'||e.keyIdentifier=='Enter'||e.keyCode==13)
	{
		if(e.target.nodeName=='INPUT'&&e.target.type=='number')
		{
			e.preventDefault();
			return false;}}},true);

window.onload = function setdate(){
  var field = document.getElementById("date");
  var date = new Date();
  field.value = date.getFullYear().toString() + '-' + (date.getMonth() + 1).toString().padStart(2, 0) +
    '-' + date.getDate().toString().padStart(2, 0);
  // console.log(field.value);
}

//all event listeners

//For all checkboxes
var total_checks = document.getElementsByClassName('check');
for (let i = 0; i < total_checks.length; i++) {
  total_checks[i].addEventListener('onchange', changed);
}

//For all col2 number inputs
var to_modify_vals = document.querySelectorAll('#participants > .checkbox-1 > .col2 > input');
var col3_for_exact = document.querySelectorAll('#participants > .checkbox-1 > .col3 > input');
for (let i = 0; i < to_modify_vals.length; i++) {
  to_modify_vals[i].addEventListener('change', inputChange);
  col3_for_exact[i].addEventListener('change', exactchange);
}

function changed(evt) {
    console.log(evt);
  
    if (evt.target.checked) {
      // var par = evt.path[3];
      var par = evt.target.parentElement.parentElement.parentElement;
      par.className = "checkbox-1 top checked"
    }
    else {
      //var par = evt.path[3];
      var par = evt.target.parentElement.parentElement.parentElement;
      par.className = "checkbox-1 bottom unchecked"
      // evt.path[2].nextElementSibling.firstElementChild.className = "modify";
      evt.target.parentElement.parentElement.nextElementSibling.firstElementChild.className = "modify";
      //evt.path[2].nextElementSibling.nextElementSibling.firstElementChild.className = "split_value0";
      evt.target.parentElement.parentElement.nextElementSibling.nextElementSibling.firstElementChild.className = "split_value0";
    }
  
    change_splits();
}

function inputChange(evt){
    evt.target.className = "nmodify";
    
    change_splits();
}

function exactchange(evt){
    evt.target.className = "split_value1";
    change_splits();
}

function change_splits(){
    var checked_given_values = document.querySelectorAll("#participants > .checked > .col2 > .nmodify");
    var checked_adjust_values = document.querySelectorAll('#participants > .checked > .col2 > .modify');

    // console.log(checked_given_values);
    // console.log(checked_adjust_values);

    var total_amount =document.querySelector("#InputAmount").valueAsNumber;
    console.log(total_amount);
    var menuName = document.querySelector('.active').innerHTML;

    var given_total_val = 0;
    var to_adjust_val = 0;

    for(let i=0; i<checked_given_values.length ; i++){
        given_total_val += checked_given_values[i].value;
    }
    if(menuName == 'Equal'){
        //We just need to set split value in col3
        var col3_adjust = document.querySelectorAll('#participants > .checked > .col3 > input');
        var col3_null = document.querySelectorAll('#participants > .unchecked > .col3 >input');
        console.log("ENtered");
        var split = Math.round((total_amount/checked_adjust_values.length).toFixed(2));
        console.log(split);
        for(let i=0; i< col3_adjust.length; i++){
            col3_adjust[i].value = split;
        }
        for(let  i =0; i< col3_null.length; i++){
            col3_null[i].value = 0;
        }

    }else if(menuName == 'Exact'){
        //We need to adjust remaining col3 values equally
        var col3_user_given = document.querySelectorAll('.checked > .col3 > .split_value1');
        var col3_adjust = document.querySelectorAll('.checked > .col3> .split_value0');
        console.log(col3_user_given);
        console.log(col3_adjust);

        var col3_null = document.querySelectorAll('.unchecked > .col3 > input');
        var user_exact_value = 0;
        for(let i=0; i<col3_user_given.length; i++){
			if(col3_user_given[i].valueAsNumber<=0){
				make_equal();
				return;
			}
            user_exact_value += col3_user_given[i].valueAsNumber;
        }
        console.log(user_exact_value);

        if(user_exact_value <= total_amount){
            var val_remaining = total_amount - user_exact_value;
            val_remaining = parseFloat(val_remaining);
            console.log(val_remaining);
            if(col3_adjust.length == 0){
              col3_user_given[col3_user_given.length-1].valueAsNumber = (col3_user_given[col3_user_given.length-1].valueAsNumber+ val_remaining).toFixed(2);
            }else{
              var split = (val_remaining/col3_adjust.length).toFixed(2);
              console.log(split);
              for(let i=0; i<col3_adjust.length; i++){
                col3_adjust[i].value = split;
              }
            }
        }else{
          //Given exact values exceeds total amount
          display_error("Dont give total larger than actual total amount");
          make_equal();
        }
        for(let i=0; i<col3_null.length; i++){
          col3_null[i].value = 0;
        }
    }else if(menuName == 'Percent'){
        //We need to adjust percentages and simultaneously their col3 values
        var user_given_percent = document.querySelectorAll('.checked > .col2 > .nmodify');
        var adjust_percent = document.querySelectorAll('.checked > .col2 > .modify');

        console.log(user_total_percent);
        console.log(adjust_percent);

        var percent_null_col2 = document.querySelectorAll('.unchecked > .col2 > input');
        var percent_null_col3 = document.querySelectorAll('.unchecked > .col3 > input');

        var user_total_percent = 0;
        for(let i =0; i< user_given_percent.length; i++){
			if(user_given_percent[i].valueAsNumber<=0){
				make_equal();
				return;
			}
          user_total_percent += user_given_percent[i].valueAsNumber;
        }
        if(user_total_percent <=100){
          var remain_percent = 100 - user_total_percent;
          console.log(remain_percent);
          
          if(adjust_percent.length == 0){
            user_given_percent[user_given_percent.length -1].valueAsNumber += remain_percent;
          }else{
            var each_percent = (remain_percent/adjust_percent.length).toFixed(2);
            console.log(each_percent);
            for(let i=0; i<adjust_percent.length ; i++){
              adjust_percent[i].value = each_percent;
            }
            adjust_percent[adjust_percent.length - 1].value = (adjust_percent[adjust_percent.length - 1].valueAsNumber + 100 - (user_total_percent+each_percent*adjust_percent.length)).toFixed(2);
          }
          adjust_amounts();
        }else{
          display_error("Percentages don't add upto 100");
          make_equal();
        
        }

        for(let i=0; i<percent_null_col2.length; i++){
          console.log(percent_null_col2[i]);
          percent_null_col2[i].value = 0;
          percent_null_col3[i].value = 0;
        }


    }else if(menuName == 'Shares'){
        //We need to adjust shares and simultaneously their col3 values
        var all_checked_shares = document.querySelectorAll('.checked > .col2 > input');
        var all_unchecked_shares = document.querySelectorAll('.unchecked > .col2 > input, .unchecked > .col3 > input');
        console.log(all_unchecked_shares);

        for(let i=0; i<all_unchecked_shares.length ; i++){
          all_unchecked_shares[i].value = 0;
        }

        var total_share=0;
        for(let i=0; i<all_checked_shares.length; i++){
          total_share +=all_checked_shares[i].valueAsNumber;
        }
        if(total_share < document.querySelectorAll('.checked > .col2 > input').length){
          // display_error("Give atleast a share of 1 for each selected consumer");
          make_equal();
        }else{
          adjust_amounts(total_share);
        }

    }else if(menuName == 'Adjust'){
        //We need to adjust col2 and simultaneously their col3 values
        var user_adjust_vals = document.querySelectorAll('.checked > .col2 > .nmodify');
        var need_to_adjust = document.querySelectorAll('.checked > .col2 > .modify');

        var adjust_null = document.querySelectorAll('.unchecked > .col2 > input , .unchecked > .col3 > input');
        var user_adjusted = 0;
        for(let i=0; i<user_adjust_vals.length; i++){
          user_adjusted += user_adjust_vals[i].valueAsNumber;
        }
        if(user_adjusted <= total_amount){
          for(let i=0; i<user_adjust_vals.length; i++){
            user_adjust_vals[i].parentElement.nextElementSibling.firstElementChild.value = user_adjust_vals[i].valueAsNumber;
          }
          for(let i=0; i<need_to_adjust.length; i++){
            need_to_adjust[i].parentElement.nextElementSibling.firstElementChild.value = 0;
          }
          adjust_amounts(user_adjusted);
        }else{
          display_error("Dont give Adjust that add up to more than total amount");
          make_equal();
        }

        for(let i=0; i<adjust_null.length ; i++){
          adjust_null[i].value = 0;
        }
    }
}



function Checkvalue(){
    var amount = document.getElementById("InputAmount");

    if (amount.value.length != 0) {
        var vals = document.getElementsByClassName("final__details");
        for (let i = 0; i < vals.length; i++) {
          if (vals[i].id == "participants") {
            vals[i].style.display = "flex";
          } else {
            vals[i].style.display = "block";
          }
    
        }
    }

    make_equal();
}

function openmenu(evt,menu){
    // var divs = document.querySelectorAll("#participants > .checked > *");
    // var total_consumers = document.querySelectorAll("#participants input:checked");
    // var c_len = total_consumers.length;
    document.querySelector('.active').className = "tablinks";
    evt.target.className = "tablinks active";
	document.querySelector("#expensetype").value=menu;
    make_equal();
}

function make_equal(){
  var divs = document.querySelectorAll("#participants > .checked > *");
  var empty_divs = document.querySelectorAll('#participants > .unchecked > .col2');
  console.log(empty_divs);
  var total_consumers = document.querySelectorAll("#participants input:checked");
  console.log(total_consumers.length);
  var c_len = total_consumers.length;
  var total_amount = document.querySelector("#InputAmount").valueAsNumber;
  var split = Math.round((total_amount/c_len).toFixed(2));
  console.log(total_amount);
  console.log(split);
  var menuName = document.querySelector('.active').innerHTML;

  if (menuName == "Equal") {

    for (let i = 0; i < divs.length; i++) {
      if (i % 3 == 1) {
        divs[i].style.display = "none";
      }
      if (i % 3 == 2) {
        var in_value = divs[i].querySelector("input");
        in_value.value = split;
        in_value.readOnly = true;
      }
    }
    for(let i=0; i<empty_divs.length; i++){
      empty_divs[i].style.display = "none";
    }

    document.querySelector('.checkbox-1 > .col2').style.display ='none';
  } else if (menuName == "Exact") {
    for (let i = 0; i < divs.length; i++) {
      if (i % 3 == 1) {
        divs[i].style.display = "none";
      }
      if (i % 3 == 2) {

        var in_value = divs[i].querySelector("input");
        in_value.value = split;
        in_value.readOnly = false;
      }
    }

    for(let i=0; i<empty_divs.length; i++){
      empty_divs[i].style.display = "none";
    }
    document.querySelector('.checkbox-1 > .col2').style.display ='none';
    rever_exact();
  }
  else if (menuName == "Percent") {
    var percent = (100 / c_len).toFixed(2);
    console.log("Entered")
    for (let i = 0; i < divs.length; i++) {
      if (i % 3 == 1) {
        divs[i].style.display = "block";
        divs[i].firstElementChild.value = percent;
      }
      if (i % 3 == 2) {
        var in_value = divs[i].querySelector("input");
        in_value.value = split;
      }
    }

    for(let i=0; i < empty_divs.length; i++ ){
        empty_divs[i].firstElementChild.value = 0;
        empty_divs[i].style.display = 'block';
    }

    document.querySelector('.checkbox-1 > .col2').style.display ='block';

  } else if (menuName == "Shares") {
    for (let i = 0; i < divs.length; i++) {
      if (i % 3 == 1) {
        divs[i].style.display = "block";
        console.log(divs[i].firstElementChild)
        divs[i].firstElementChild.value = 1;
      }
      if (i % 3 == 2) {
        var in_value = divs[i].querySelector("input");
        in_value.value = split;
      }
    }

    for(let i=0; i < empty_divs.length; i++ ){
        empty_divs[i].firstElementChild.value = 0;
        empty_divs[i].style.display = 'block';
    }
    
    document.querySelector('.checkbox-1 > .col2').style.display ='block';

  } else if (menuName == "Adjust") {
    for (let i = 0; i < divs.length; i++) {
      if (i % 3 == 1) {
        divs[i].style.display = "block";
        divs[i].firstElementChild.value = 0;
      }
      if (i % 3 == 2 ) {
        var in_value = divs[i].querySelector("input");
        in_value.value = split;
      }
    }

    for(let i=0; i < empty_divs.length; i++ ){
        empty_divs[i].firstElementChild.value = 0;
        empty_divs[i].style.display = 'block';
    }
    
    document.querySelector('.checkbox-1 > .col2').style.display ='block';
  }
  //revert to modify 
  revert_modify();

}

function adjust_amounts(total_val){
  var menuName = document.querySelector('.active').innerHTML;
  var total_amount = document.getElementById("InputAmount").valueAsNumber;

  var all_checked_values = document.querySelectorAll('.checked > .col2 > input, .checked > .col3 > input');
  console.log(all_checked_values);

  if(menuName == 'Percent'){
    // var assigned_sum = 0;
    for(let i=0; i<all_checked_values.length-1; i = i+2){
      all_checked_values[i+1].value = ((all_checked_values[i].valueAsNumber/100)*total_amount).toFixed(2);
      // assigned_sum += ((all_checked_values[i].valueAsNumber/100)*total_amount).toFixed(2);
    }
    // all_checked_values[all_checked_values.length-1].value += total_amount - assigned_sum; 
  }else if(menuName == 'Shares'){
    console.log(total_val);
    for(let i=0; i<all_checked_values.length; i=i+2){
      all_checked_values[i+1].value = ((all_checked_values[i].valueAsNumber/total_val)*total_amount).toFixed(2);
    }
  }else if(menuName == 'Adjust'){
    console.log(total_val);
    total_amount = total_amount - total_val;
    var equal_split = (total_amount/(all_checked_values.length/2)).toFixed(2);
    equal_split = parseFloat(equal_split);
    console.log(equal_split);
    for(let i=0; i<all_checked_values.length; i=i+2){
      all_checked_values[i+1].valueAsNumber = (all_checked_values[i+1].valueAsNumber+ equal_split).toFixed(2);
    }
    
  }
}

function revert_modify(){
    var to_modify_vals = document.querySelectorAll('#participants > .checkbox-1 > .col2 > input');

    for (let i = 0; i < to_modify_vals.length; i++) {
      to_modify_vals[i].className = "modify";
    }
  
}

function rever_exact(){
  var to_modify_vals = document.querySelectorAll('#participants > .checkbox-1 > .col3 > input');

  for(let i=0; i<to_modify_vals.length ; i++){
    to_modify_vals[i].className = "split_value0";
  }
}


function display_error(msg){
  document.getElementById("message").innerHTML = msg;

  setTimeout(function(){
      document.getElementById("message").innerHTML = '';
  }, 4000);

}
