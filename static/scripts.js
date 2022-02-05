// our updatable variable objects to use globally
let img = {};
let position = {};

// image matrix function to update img object variable
function imgMatrix() {

  // our image object inside area
  let $img = $('IMG', '.area');

  // offset data of image
  let offset = $img.offset();

  // add/update object key data
  img.width = $img.outerWidth();
  img.height = $img.outerHeight();
  img.offsetX = offset.left - $(document).scrollLeft();
  img.offsetY = offset.top - $(document).scrollTop();

}

// position matrix function to update position object variable
function positionMatrix(e, mousedown = false) {

  // if mousedown param is true... for use in 
  if (mousedown) {

    // set the top/left position object data with percentage position
    position.top = (100 / img.height) * ( (e.pageY - $(document).scrollTop()) - img.offsetY);
    position.left = (100 / img.width) * ( (e.pageX - $(document).scrollLeft()) - img.offsetX);

  }

  // set the right/bottom position object data with percentage position
  position.right = 100 - ((100 / img.width) * ((e.pageX - $(document).scrollLeft()) - img.offsetX));
  position.bottom = 100 - ((100 / img.height) * ((e.pageY - $(document).scrollTop()) - img.offsetY));

}

// mouse move event function in area div
$(document).on('mousemove', '.area', function(e) {

  // / update img object variable data upon this mousemove event
  imgMatrix();

  // if this area has draw class
  if ($(this).hasClass('draw')) {

    // update position object variable data passing current event data
    positionMatrix(e);

    // if image x cursor drag position percent is negative to mousedown x position
    if ((100 - position.bottom) < position.top) {

      // update rectange x negative positions css
      $('.rect', this).css({
        top: (100 - position.bottom) + '%',
        bottom: (100 - position.top) + '%'
      });

      // else if image x cursor drag position percent is positive to mousedown x position
    } else {

      // update rectange x positive positions css
      $('.rect', this).css({
        bottom: position.bottom + '%',
        top: position.top + '%',
      });

    }

    // if image y cursor drag position percent is negative to mousedown y position
    if ((100 - position.right) < position.left) {

      // update rectange y negative positions css
      $('.rect', this).css({
        left: (100 - position.right) + '%',
        right: (100 - position.left) + '%'
      });

      // else if image y cursor drag position percent is positive to mousedown y position
    } else {

      // update rectange y positive positions css
      $('.rect', this).css({
        right: position.right + '%',
        left: position.left + '%'
      });

    }

  }

});

// mouse down event function in area div
$(document).on('mousedown', '.area', function(e) {

  // remove the drawn class
  $(this).removeClass('drawn');

  // update img object variable data upon this mousedown event
  imgMatrix();

  // update position object variable data passing current event data and mousedown param as true 
  positionMatrix(e, true);

  // update rectange xy positions css
  $('.rect', this).css({
    left: position.left + '%',
    top: position.top + '%',
    right: position.right + '%',
    bottom: position.bottom + '%'
  });

  // add draw class to area div to reveal rectangle
  $(this).addClass('draw');

});

// mouse up event function in area div
$(document).on('mouseup', '.area', function(e) {

  // update img object variable data upon this mouseup event
  imgMatrix();

  // if this area had draw class
  if ($(this).hasClass('draw')) {

    // update position object variable data passing current event
    positionMatrix(e);

    // math trunc on position values if x and y values are equal, basically no drawn rectangle on mouseup event
    if ((Math.trunc(position.left) === Math.trunc(100 - position.right)) && (Math.trunc(position.top) === Math.trunc(100 - position.bottom))) {
      
      // remove draw and drawn classes
      $(this).removeClass('draw drawn');

    // else if x and y values are not equal, basically a rectange has been drawn
    } else {

      // add drawn class and remove draw class
      $(this).addClass('drawn').removeClass('draw');

    }

  }

});

// on window resize function
$(window).on('resize', function(e) {
  
  // update img object variable data upon this window resize event
  imgMatrix();

});
