var cookie_panels = 'activeGroups';
var is_open_sidenav = false;

function open_panel(group_str, anchor) {
  var groups = group_str.split(',');
  for (var i = 0, len = groups.length; i < len; i++) {
    var grp = $('#' + groups[i]);
    grp.collapse({
      toggle: false
    });
    grp.collapse('show');
  }
  var tag = $('#' + anchor);
  $('html,body').animate({scrollTop: tag.offset().top}, 'slow');
}

function get_opened_panels(groupids) {
  var ids = groupids.split(',');
  var lst = '';
  for (var i = 0, len = ids.length; i < len; i++) {
    var id = ids[i];
    var grp = $('#' + id);
    var opened = grp.hasClass('in');
    if (opened) {
      if (lst !== '') {
        lst = lst + ',' + id;
      } else {
        lst = id;
      }
    }
  }
  return lst;
}

function restore_panels(groupids, openids) {
  if (openids !== undefined) {
    var ids = groupids.split(',');
    var open_ids = openids.split(',');
    for (var i = 0, len = ids.length; i < len; i++) {
      var id = ids[i];
      var grp = $('#' + id);
      grp.collapse({toggle: false});
      var n = $.inArray(id, open_ids);
      if (n > -1) {
        grp.collapse('show');
      } else {
        grp.collapse('hide');
      }
    }
  }
}

function prefix(msg) {
  return '<br/><i class="fas fa-info-circle" aria-hidden="true"></i> ' + msg;
}

function save_open_panels(ids) {
  Cookies.set(cookie_panels, get_opened_panels(ids), {SameSite: 'strict'});
}
