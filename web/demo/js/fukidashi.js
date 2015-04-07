enchant();

function create_fukidashi(message, x, y, color){
  height = 47 * (1 + (message.length / 30));
  fukidashi = new TBalloon(800, height, TBalloon.BOTTOM, TBalloon.CENTER, color);
  fukidashi.x = x;
  fukidashi.y = y;
  fukidashi.text(message);
  return fukidashi;
}


// ふきだしクラス
// Ref: http://v416.hateblo.jp/entry/2012/10/19/225500
TBalloon = enchant.Class.create(enchant.Sprite, {
  initialize : function(w, h, line, align, color) {
    enchant.Sprite.call(this, w, h + TBalloon.TAIL);
    this.line = line;
    this.align = align;
    this.image = new Surface(w, h + TBalloon.TAIL);
    this.liner = new Surface(w, h);
    var t = TBalloon.TAIL;
    var s = TBalloon.SIZE;
    var c = TBalloon.CURVE;
    this.outCurve = {
      lt : {x:0, y:0},
      rt : {x:w, y:0},
      rd : {x:w, y:h},
      ld : {x:0, y:h}
    };
    this.inCurve = {
      lt : {x:0+s, y:0+s},
      rt : {x:w-s, y:0+s},
      rd : {x:w-s, y:h-s},
      ld : {x:0+s, y:h-s}
    };
    var o = this.outCurve;
    var i = this.inCurve;

    with(this.liner.context) {
      fillStyle = '#aaaaaa';
      strokeStyle = '#aaaaa';
      beginPath();
      moveTo(o.lt.x, o.lt.y+c);
      quadraticCurveTo(o.lt.x, o.lt.y, o.lt.x+c, o.lt.y);
      lineTo(o.rt.x-c, o.rt.y);
      quadraticCurveTo(o.rt.x, o.rt.y, o.rt.x, o.rt.y+c);
      lineTo(o.rd.x, o.rd.y-c);
      quadraticCurveTo(o.rd.x, o.rd.y, o.rd.x-c, o.rd.y);
      lineTo(o.ld.x+c, o.ld.y);
      quadraticCurveTo(o.ld.x, o.ld.y, o.ld.x, o.ld.y-c);
      closePath();
      fill();
      stroke();
      // 抜く
      fillStyle = color;
      beginPath();
      moveTo(i.lt.x, o.lt.y+c);
      quadraticCurveTo(i.lt.x, i.lt.y, o.lt.x+c, i.lt.y);
      lineTo(o.rt.x-c, i.rt.y);
      quadraticCurveTo(i.rt.x, i.rt.y, i.rt.x, o.rt.y+c);
      lineTo(i.rd.x, o.rd.y-c);
      quadraticCurveTo(i.rd.x, i.rd.y, o.rd.x-c, i.rd.y);
      lineTo(o.ld.x+c, i.ld.y);
      quadraticCurveTo(i.ld.x, i.ld.y, i.ld.x, o.ld.y-c);
      closePath();
      fill();
    };
    // しっぽ
    var b = {
      x:this.align==TBalloon.LEFT ?TBalloon.HORN:
        this.align==TBalloon.RIGHT?this.width-TBalloon.HORN:this.width/2,
      y:this.line==TBalloon.TOP?0:this.height
    };
    var triangle = {
      c:{x:b.x  ,y:b.y},
      l:{x:b.x-TBalloon.TAIL/2,y:b.y+(this.line==TBalloon.TOP?1:-1)*TBalloon.TAIL},
      r:{x:b.x+TBalloon.TAIL/2,y:b.y+(this.line==TBalloon.TOP?1:-1)*TBalloon.TAIL}
    };
    with(this.image.context) {
      fillStyle = '#aaaaaa';
      strokeStyle = '#aaaaaa';
      beginPath();
      moveTo(triangle.l.x,triangle.l.y);
      lineTo(triangle.c.x,triangle.c.y);
      lineTo(triangle.r.x,triangle.r.y);
      closePath();
      fill();
      stroke();
    };
    //this.clear();
  },
  clear : function() {
    this.image.draw(this.liner, 0, this.line == TBalloon.TOP ? TBalloon.TAIL : 0);
  },
  text : function(text) {
    this.clear();
    with(this.image.context) {
      font = 'bold 23px "メイリオ",Meiryo,"ヒラギノ角ゴ Pro W3","Hiragino Kaku Gothic Pro","HiraKaku Pro-W3",Arial,Helvetica,sans-serif';
      fillStyle = '#666666';
      textAlign = 'center';
      textBaseline = 'middle';
      buf = "";
      divide = Math.floor(text.length / 29) + 1;
      divide_count = 0;
      for (i = 0, len = text.length; i < len; i++) {
        buf += text.charAt(i);
        if (i > 0 && (i % 29) == 0){
          ++divide_count;
          height = this.height * (divide_count / divide) - this.height * 0.1;
          fillText(buf,this.width/2, height);
          buf = "";
        }
      }
      if (buf != null){
        if (divide == 1){
          height = this.height/2 - (this.line==TBalloon.TOP?0:TBalloon.TAIL);
        }
        else {
          ++divide_count;
          height = this.height * (divide_count / divide) - this.height * 0.1;
        }
        fillText(buf, this.width/2, height);
      }
    };
  }
});
TBalloon.TAIL   =  0;
TBalloon.SIZE   =  2;
TBalloon.CURVE  = 16;
TBalloon.HORN   = 16;
TBalloon.TOP    = "top";
TBalloon.BOTTOM = "bottom";
TBalloon.CENTER = "center";
TBalloon.LEFT   = "left";
TBalloon.RIGHT  = "right";
