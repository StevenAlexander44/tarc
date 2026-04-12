var proto_initIcon=L.Marker.prototype._initIcon;
var proto_setPos=L.Marker.prototype._setPos;
L.Marker.addInitHook(function(){
  this.options.rotationAngle=this.options.rotationAngle||0;
  this.on('drag',function(e){e.target._applyRotation()});
});
L.Marker.include({
  _initIcon:function(){
    proto_initIcon.call(this);
  },
  _setPos:function(pos){
    proto_setPos.call(this,pos);
    this._applyRotation();
  },
  _applyRotation:function(){
    if(this.options.rotationAngle){
      this._icon.style[L.DomUtil.TRANSFORM]+=` rotateZ(${this.options.rotationAngle-90}deg)`;
      this._icon.style[L.DomUtil.TRANSFORM+'Origin']='50% 50%';
    }
  },
  setRotationAngle:function(angle){
    this.options.rotationAngle=angle;
    this.update();
    return this;
  }
});
